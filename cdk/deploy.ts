import "source-map-support/register";
import path from "path";
import { GetCallerIdentityCommand, STSClient } from "@aws-sdk/client-sts";
import { aws_events, aws_events_targets, aws_iam, aws_lambda, aws_s3, App, Duration, Stack, StackProps, RemovalPolicy } from "aws-cdk-lib";
import { Construct } from "constructs";
import { Platform } from "aws-cdk-lib/aws-ecr-assets";

Error.stackTraceLimit = Infinity;

const environmetKeys = [
  "ENV_NAME",
  "DOMAIN",
  "READ_ACCESS_TOKEN",
  "WRITE_ACCESS_TOKEN",
  "S3_BUCKET",
] as const;

type Env = { [key in typeof environmetKeys[number]]: string };

function parseEnv() {
  const targets = [...environmetKeys];

  return targets.reduce((obj, target) => {
    obj[target] = process.env[target] || "";
    return obj;
  }, {} as Env);
}

function checkEnv(env: Env) {
  const required: Partial<typeof environmetKeys> = [
    "ENV_NAME",
    "DOMAIN",
    "READ_ACCESS_TOKEN",
    "WRITE_ACCESS_TOKEN"
  ];
  for (const key of required) {
    if (key && !env[key]) {
      throw new Error(`環境変数 '${key}' が設定されていません。.envファイルを確認してください。`);
    }
  }
}

export class NafStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps, env: Env) {
    super(scope, id, props);

    const isX64 = process.arch === "x64";
    const lambdaArchitecture = isX64 ? aws_lambda.Architecture.X86_64 : aws_lambda.Architecture.ARM_64;
    const lambdaPlatform = isX64 ? Platform.LINUX_AMD64 : Platform.LINUX_ARM64;

    const role = new aws_iam.Role(this, "MarkovBotFunctionRole", {
      roleName: `markovbot-${env.ENV_NAME}-function-role`,
      assumedBy: new aws_iam.ServicePrincipal("lambda.amazonaws.com"),
      managedPolicies: [
        aws_iam.ManagedPolicy.fromAwsManagedPolicyName("CloudWatchLogsFullAccess"),
      ],
    });

    const s3 = new aws_s3.Bucket(this, "S3Bucket", {
      encryption: aws_s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: aws_s3.BlockPublicAccess.BLOCK_ALL,
      autoDeleteObjects: true,
      removalPolicy: RemovalPolicy.DESTROY,
    });
    env.S3_BUCKET = s3.bucketName;

    const lambda = new aws_lambda.Function(this, "MarkovBotFunction", {
      runtime: aws_lambda.Runtime.FROM_IMAGE,
      architecture: lambdaArchitecture,
      memorySize: 1536,
      timeout: Duration.minutes(10),
      code: aws_lambda.Code.fromAssetImage(path.resolve("../"), {
        platform: lambdaPlatform,
        file: "lambda.Dockerfile",
      }),
      handler: aws_lambda.Handler.FROM_IMAGE,
      environment: env,
      role,
    });
    s3.grantReadWrite(lambda);

    const schedulerRule = new aws_events.Rule(this, "MarkovBotFunctionSchedulerEvent", {
      schedule: aws_events.Schedule.cron({
        minute: "0/20",
      }),
    });
    schedulerRule.addTarget(new aws_events_targets.LambdaFunction(lambda));
  }
}

(async () => {
  const env = parseEnv();
  checkEnv(env);

  const account = await new STSClient({}).send(new GetCallerIdentityCommand({}));

  const app = new App();
  const stack = new NafStack(
    app,
    `markovbot-${env.ENV_NAME}`,
    {
      env: {
        account: account.Account,
        region: process.env.AWS_REGION || "ap-northeast-1",
      },
    },
    env,
  );
})();
