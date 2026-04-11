import paramiko

SERVER_IP = "43.251.225.175"
SERVER_USER = "root"
SERVER_PASSWORD = "fiueBRDM1951"
SERVER_PORT = 22

DB_NAME = "alpha_arena"
DB_USER = "alpha_user"
DB_PASSWORD = "alpha_pass"

OUTPUT_FILE = "memory_records_result.txt"


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
    log("查询 hyper_ai_memory 表 (用户记忆)")
    log("="*80)
    
    count_query = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -t -A -c "
    SELECT COUNT(*) FROM hyper_ai_memory
    " """
    
    stdin, stdout, stderr = ssh.exec_command(count_query)
    result = stdout.read().decode('utf-8').strip()
    log(f"\n记忆总数: {result} 条\n")
    
    memory_query = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -t -A -F'|' -c "
    SELECT id, category, content, source, importance, is_active, created_at, updated_at
    FROM hyper_ai_memory
    ORDER BY importance DESC, created_at DESC
    " """
    
    stdin, stdout, stderr = ssh.exec_command(memory_query)
    result = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if error and 'error' in error.lower():
        log(f"错误: {error}")
        return
    
    log("-" * 80)
    for line in result.strip().split('\n'):
        if line.strip():
            parts = line.split('|')
            if len(parts) >= 8:
                log(f"\n记忆ID: {parts[0].strip()}")
                log(f"  类别: {parts[1].strip()}")
                log(f"  内容: {parts[2].strip()}")
                log(f"  来源: {parts[3].strip()}")
                log(f"  重要性: {parts[4].strip()}")
                log(f"  是否活跃: {parts[5].strip()}")
                log(f"  创建时间: {parts[6].strip()}")
                log(f"  更新时间: {parts[7].strip()}")
                log("-" * 80)
    
    log("\n" + "="*80)
    log("查询 hyper_ai_profile 表 (用户配置)")
    log("="*80)
    
    profile_query = f"""docker exec hyper-arena-postgres psql -U {DB_USER} -d {DB_NAME} -t -A -F'|' -c "
    SELECT id, nickname, trading_style, risk_preference, experience_level, 
           preferred_symbols, preferred_timeframe, capital_scale,
           onboarding_completed, llm_provider, llm_model,
           created_at, updated_at
    FROM hyper_ai_profile
    " """
    
    stdin, stdout, stderr = ssh.exec_command(profile_query)
    result = stdout.read().decode('utf-8')
    
    for line in result.strip().split('\n'):
        if line.strip():
            parts = line.split('|')
            if len(parts) >= 13:
                log(f"\n用户配置ID: {parts[0].strip()}")
                log(f"  昵称: {parts[1].strip()}")
                log(f"  交易风格: {parts[2].strip()}")
                log(f"  风险偏好: {parts[3].strip()}")
                log(f"  经验水平: {parts[4].strip()}")
                log(f"  偏好币种: {parts[5].strip()}")
                log(f"  偏好周期: {parts[6].strip()}")
                log(f"  资金规模: {parts[7].strip()}")
                log(f"  入门完成: {parts[8].strip()}")
                log(f"  LLM提供商: {parts[9].strip()}")
                log(f"  LLM模型: {parts[10].strip()}")
                log(f"  创建时间: {parts[11].strip()}")
                log(f"  更新时间: {parts[12].strip()}")
    
    log("\n\n" + "="*80)
    log("查询完成!")
    log("="*80)
    log("\n记忆数据存储在服务器数据库中:")
    log(f"  服务器: {SERVER_IP}")
    log(f"  数据库: {DB_NAME}")
    log(f"  表名:")
    log(f"    - hyper_ai_memory (用户记忆表)")
    log(f"    - hyper_ai_profile (用户配置表)")
    
    ssh.close()
    log("\nSSH连接已关闭")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    print(f"\n结果已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
