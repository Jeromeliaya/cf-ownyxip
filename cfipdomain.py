import requests
import json
import CloudFlare

def get_cf_ip_top20_json():
    # 发送 HTTP 请求
    response = requests.get("https://vps789.com/vps/sum/cfIpTop20")

    # 检查响应状态码
    if response.status_code == 200:
        # 返回 JSON 数据
        return response.json()
    else:
        # 返回 None 表示请求失败
        return None

def parse_cf_ip_top20():
    # 获取优选IP
    data = get_cf_ip_top20_json()

    # 提取服务器信息
    servers = data["data"]["good"]

    # 选丢包率小于1的IP
    ip_addresses = []
    for server in servers:
        if server["avgPkgLostRate"] < 1:
            ip_addresses.append(server["ip"])

    return ip_addresses

# 获取优选IP
ip_addresses = parse_cf_ip_top20()

# Cloudflare API 凭证
cloudflare_api_key = "替换你CF的API密钥"
cloudflare_email = "替换你登录CF的邮箱"
zone_id = "你域名的区域ID"

# 域名
domain_name = "替换你在cf托管的域名，比如dabo.free.hr"
# DNS 记录名称
record_short_name = "替换你的dns名称，比如cfip"
# 优选域名全名称
record_name = "替换你的域名全称 比如cfip.dabo.free.hr"

# 要添加的 DNS 记录
dns_records = []
for ip_address in ip_addresses:
    print(ip_address)
    dns_record = {
            "type": "A",
            "name": record_short_name,
            "content": ip_address,
            "ttl": 120,
            "proxied": False,
        }
    dns_records.append(dns_record)

            
cf = CloudFlare.CloudFlare(cloudflare_email, cloudflare_api_key)
    
# 删除记录
record_type = 'A'
old_dns_records = cf.zones.dns_records.get(zone_id, params={'name': record_name, 'type': record_type})
print('开始删除DNS记录')
for record in old_dns_records:
    print(record['id'], record['name'], record['type'], record['content'])
    dns_record_id = record['id']
    cf.zones.dns_records.delete(zone_id, dns_record_id)
print('删除DNS记录完成')

# 添加记录
print('开始添加新的DNS记录')
for dns_record in dns_records:
    try:
        print(dns_record['content'])
        r = cf.zones.dns_records.post(zone_id, data=dns_record)
    except CloudFlare.CloudFlareAPIError as e:
        exit('/zones.dns_records.post %s - %d %s' % (record['name'], e, e))
print('添加新的DNS记录成功')