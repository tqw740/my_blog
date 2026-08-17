import uuid
from datetime import datetime
import boto3
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings

# 初始化 S3 客户端（针对 R2）
s3_client = boto3.client(
    's3',
    endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    region_name='auto',
)

@login_required  # 必须保证只有博主/管理员能调用
def get_upload_presigned_url(request):
    filename = request.GET.get('filename', 'image.png')
    content_type = request.GET.get('content_type', 'image/jpeg')
    
    # 提取后缀并生成唯一 key（按年月归档）
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'png'
    key = f"posts/{datetime.now().strftime('%Y/%m')}/{uuid.uuid4().hex}.{ext}"

    # 生成预签名 PUT URL（有效期 5 分钟）
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.R2_BUCKET_NAME,
            'Key': key,
            'ContentType': content_type,
        },
        ExpiresIn=300
    )

    # 最终的公开访问链接
    public_url = f"https://{settings.R2_CUSTOM_DOMAIN}/{key}"

    return JsonResponse({
        'upload_url': presigned_url,
        'public_url': public_url
    })