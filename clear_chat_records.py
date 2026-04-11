import paramiko

SERVER_IP = "43.251.225.175"
SERVER_USER = "root"
SERVER_PASSWORD = "fiueBRDM1951"
SERVER_PORT = 22

DB_NAME = "alpha_arena"
DB_USER = "alpha_user"
DB_PASSWORD = "alpha_pass"


def main():
    print(f"正在连接服务器 {SERVER_IP}...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_IP, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD)
    print("SSH连接成功!\n")
    
    print("="*80)
    print("清空前统计")
    print("="*80)
    
    count_query = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -t -A -c "
    SELECT 
        (SELECT COUNT(*) FROM hyper_ai_messages) as messages,
        (SELECT COUNT(*) FROM hyper_ai_conversations) as conversations
    " """
    
    stdin, stdout, stderr = ssh.exec_command(count_query)
    result = stdout.read().decode('utf-8').strip()
    
    if result:
        parts = result.split('|')
        if len(parts) >= 2:
            print(f"消息数量: {parts[0].strip()}")
            print(f"会话数量: {parts[1].strip()}")
    
    print("\n" + "="*80)
    print("正在清空聊天记录...")
    print("="*80)
    
    delete_messages = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -c "
    DELETE FROM hyper_ai_messages;
    " """
    
    stdin, stdout, stderr = ssh.exec_command(delete_messages)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if 'DELETE' in result:
        print("✓ hyper_ai_messages 表已清空")
    else:
        print(f"清空消息表时出错: {error}")
    
    delete_conversations = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -c "
    DELETE FROM hyper_ai_conversations;
    " """
    
    stdin, stdout, stderr = ssh.exec_command(delete_conversations)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if 'DELETE' in result:
        print("✓ hyper_ai_conversations 表已清空")
    else:
        print(f"清空会话表时出错: {error}")
    
    print("\n" + "="*80)
    print("清空后验证")
    print("="*80)
    
    stdin, stdout, stderr = ssh.exec_command(count_query)
    result = stdout.read().decode('utf-8').strip()
    
    if result:
        parts = result.split('|')
        if len(parts) >= 2:
            print(f"消息数量: {parts[0].strip()}")
            print(f"会话数量: {parts[1].strip()}")
    
    ssh.close()
    print("\n✓ 历史聊天记录已全部清空!")
    print("SSH连接已关闭")


if __name__ == "__main__":
    main()
