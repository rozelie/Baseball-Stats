# Setup: https://earthly.dev/blog/deploy-dockcontainers-to-awsecs-using-terraform/
# Adding Logging: https://saturncloud.io/blog/terraform-aws-cloudwatch-log-group-for-ecs-taskscontainers-a-comprehensive-guide/
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.45.0"
    }
  }
}

locals {
  name         = "cobp"
  image_tag    = "latest"
  aws_region   = "us-east-1"
  service_port = 80
}

resource "aws_ecr_repository" "this" {
  name = local.name
}

resource "aws_ecs_cluster" "this" {
  name = local.name
}

resource "aws_ecs_task_definition" "this" {
  family                   = local.name
  container_definitions    = <<DEFINITION
  [
    {
      "name": "${local.name}",
      "image": "${aws_ecr_repository.this.repository_url}:${local.image_tag}",
      "essential": true,
      "portMappings": [
        {
          "containerPort": ${local.service_port},
          "hostPort": ${local.service_port}
        }
      ],
      "environment": [
        {
          "name": "SERVER_PORT",
          "value": "${local.service_port}"
        }
      ],
      "memory": 2048,
      "cpu": 256,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "${aws_cloudwatch_log_group.this.name}",
          "awslogs-region": "${local.aws_region}",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
  DEFINITION
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc" # add the AWS VPN network mode as this is required for Fargate
  memory                   = 2048
  cpu                      = 256
  execution_role_arn       = aws_iam_role.this.arn
}

resource "aws_cloudwatch_log_group" "this" {
  name = "/ecs/${local.name}"
}

resource "aws_iam_role" "this" {
  name               = "ecsTaskExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.this.json
}

data "aws_iam_policy_document" "this" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_default_vpc" "this" {
}

resource "aws_default_subnet" "default_subnet_a" {
  availability_zone = "${local.aws_region}a"
}

resource "aws_default_subnet" "default_subnet_b" {
  availability_zone = "${local.aws_region}b"
}

resource "aws_alb" "this" {
  name               = local.name
  load_balancer_type = "application"
  subnets = [ # Referencing the default subnets
    "${aws_default_subnet.default_subnet_a.id}",
    "${aws_default_subnet.default_subnet_b.id}"
  ]
  security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
}

resource "aws_security_group" "load_balancer_security_group" {
  ingress {
    from_port   = local.service_port
    to_port     = local.service_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allow traffic in from all sources
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb_target_group" "this" {
  name        = "target-group"
  port        = local.service_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_default_vpc.this.id
  health_check {
    enabled = true
    path    = "/healthz"
  }
}

resource "aws_lb_listener" "this" {
  load_balancer_arn = aws_alb.this.arn
  port              = local.service_port
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

resource "aws_ecs_service" "this" {
  name                              = local.name
  cluster                           = aws_ecs_cluster.this.id
  task_definition                   = aws_ecs_task_definition.this.arn
  launch_type                       = "FARGATE"
  desired_count                     = 1
  health_check_grace_period_seconds = 300

  load_balancer {
    target_group_arn = aws_lb_target_group.this.arn
    container_name   = aws_ecs_task_definition.this.family
    container_port   = local.service_port
  }

  network_configuration {
    subnets = [
      "${aws_default_subnet.default_subnet_a.id}",
      "${aws_default_subnet.default_subnet_b.id}"
    ]
    assign_public_ip = true                                                # Provide the containers with public IPs
    security_groups  = ["${aws_security_group.service_security_group.id}"] # Set up the security group
  }
}

resource "aws_security_group" "service_security_group" {
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    # Only allowing traffic in from the load balancer security group
    security_groups = ["${aws_security_group.load_balancer_security_group.id}"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "app_url" {
  value = aws_alb.this.dns_name
}