import boto3

from flask import current_app


def publish_message(phone, message):
    phone.replace('-', '')
    krcode = '+82'

    phone_number = krcode + '1084358100'
    client = boto3.client(
        "sns",
        aws_access_key_id=current_app.config['AWS_SNS_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['AWS_SNS_SECRET_KEY'],
        region_name=current_app.config['AWS_SNS_REGION_NAME']  # 도쿄
    )
    # # 주제에 대한 구독자 추가
    # topic_arn = current_app.config['AWS_SNS_SMS_TOPIC_ARN']
    #
    # client.subscribe(
    #     TopicArn=topic_arn,
    #     Protocol='sms',
    #     Endpoint=phone_number
    # )
    # # 주제를 구독한 사람들에게 메시지 보내기
    # client.publish(
    #     TopicArn=topic_arn,
    #     Message=message
    # )

    response = client.publish(
        PhoneNumber=phone_number,
        Message=message
    )

    print(response)
