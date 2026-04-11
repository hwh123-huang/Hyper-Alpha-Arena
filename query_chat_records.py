import paramiko
import json
from datetime import datetime

SERVER_IP = "43.251.225.175"
SERVER_USER = "root"
SERVER_PASSWORD = "fiueBRDM1951"
SERVER_PORT = 22

DB_NAME = "alpha_arena"
DB_USER = "alpha_user"
DB_PASSWORD = "alpha_pass"

OUTPUT_FILE = "chat_records_result.txt"


def main():
    output_lines = []
    
    def log(msg):
        print(msg)
        output_lines.append(msg)
    
    log(f"正在连接服务器 {SERVER_IP}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD)
    log("SSH连接成功!\n")
    
    log("="*80)
    log("查询 hyper_ai_conversations 表 (会话列表)")
    log("="*80)
    
    docker_query = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -t -A -F'|' -c "
    SELECT id, title, message_count, is_bot_conversation, bot_platform, created_at, updated_at
    FROM hyper_ai_conversations
    ORDER BY updated_at DESC
    " """
    
    stdin, stdout, stderr = ssh.exec_command(docker_query)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if error and 'error' in error.lower():
        log(f"错误: {error}")
        return
    
    conversations = []
    log(f"\n找到的会话:\n")
    for line in result.strip().split('\n'):
        if line.strip():
            parts = line.split('|')
            if len(parts) >= 7:
                conv = {
                    'id': parts[0].strip(),
                    'title': parts[1].strip(),
                    'message_count': parts[2].strip(),
                    'is_bot': parts[3].strip(),
                    'bot_platform': parts[4].strip() if parts[4].strip() else 'None',
                    'created_at': parts[5].strip(),
                    'updated_at': parts[6].strip()
                }
                conversations.append(conv)
                log(f"会话ID: {conv['id']}")
                log(f"  标题: {conv['title']}")
                log(f"  消息数: {conv['message_count']}")
                log(f"  是否Bot会话: {conv['is_bot']} (平台: {conv['bot_platform']})")
                log(f"  创建时间: {conv['created_at']}")
                log(f"  更新时间: {conv['updated_at']}")
                log("-" * 60)
    
    log("\n" + "="*80)
    log("查询 hyper_ai_messages 表 (消息详情)")
    log("="*80)
    
    for conv in conversations:
        conv_id = conv['id']
        log(f"\n{'='*60}")
        log(f"会话: {conv['title']} (ID: {conv_id})")
        log("="*60)
        
        msg_query = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -t -A -F'|' -c "
        SELECT role, substring(content, 1, 500) as content_preview, created_at
        FROM hyper_ai_messages
        WHERE conversation_id = {conv_id}
        ORDER BY created_at ASC
        " """
        
        stdin, stdout, stderr = ssh.exec_command(msg_query)
        result = stdout.read().decode('utf-8')
        
        msg_count = 0
        for line in result.strip().split('\n'):
            if line.strip():
                parts = line.split('|')
                if len(parts) >= 3:
                    msg_count += 1
                    role = parts[0].strip()
                    content = parts[1].strip()
                    created_at = parts[2].strip()
                    log(f"\n[{created_at}] {role.upper()}:")
                    log(f"  {content}")
        
        log(f"\n共 {msg_count} 条消息")
    
    log("\n\n" + "="*80)
    log("查询完成!")
    log("="*80)
    log("\n聊天记录存储在服务器数据库中:")
    log(f"  服务器: {SERVER_IP}")
    log(f"  数据库: {DB_NAME}")
    log(f"  表名:")
    log(f"    - hyper_ai_conversations (会话表)")
    log(f"    - hyper_ai_messages (消息表)")
    
    ssh.close()
    log("\nSSH连接已关闭")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    print(f"\n结果已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
