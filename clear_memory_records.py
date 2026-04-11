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
    SELECT COUNT(*) FROM hyper_ai_memory
    " """
    
    stdin, stdout, stderr = ssh.exec_command(count_query)
    result = stdout.read().decode('utf-8').strip()
    print(f"记忆数量: {result} 条\n")
    
    print("="*80)
    print("正在清空记忆数据...")
    print("="*80)
    
    delete_memory = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -c "
    DELETE FROM hyper_ai_memory;
    " """
    
    stdin, stdout, stderr = ssh.exec_command(delete_memory)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if 'DELETE' in result:
        print("✓ hyper_ai_memory 表已清空")
    else:
        print(f"清空记忆表时出错: {error}")
    
    print("\n" + "="*80)
    print("清空后验证")
    print("="*80)
    
    stdin, stdout, stderr = ssh.exec_command(count_query)
    result = stdout.read().decode('utf-8').strip()
    print(f"记忆数量: {result} 条")
    
    ssh.close()
    print("\n✓ 用户记忆数据已全部清空!")
    print("SSH连接已关闭")


if __name__ == "__main__":
    main()
