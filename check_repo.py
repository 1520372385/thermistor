import requests
import sys

def check_github_repo_exists(username, repo_name):
    """检查GitHub仓库是否存在"""
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 仓库存在: {username}/{repo_name}")
            print(f"   仓库名称: {data.get('name', 'N/A')}")
            print(f"   描述: {data.get('description', 'N/A')}")
            print(f"   可见性: {data.get('visibility', 'N/A')}")
            print(f"   私有: {data.get('private', 'N/A')}")
            print(f"   URL: {data.get('html_url', 'N/A')}")
            return True
        elif response.status_code == 404:
            print(f"❌ 仓库不存在: {username}/{repo_name}")
            print(f"   错误: {response.status_code} - {response.reason}")
            return False
        else:
            print(f"⚠️ 其他错误: {response.status_code} - {response.reason}")
            print(f"   响应: {response.text[:200]}...")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        return False

if __name__ == "__main__":
    username = "1520372385"
    repo_name = "thermistor"
    
    print(f"检查GitHub仓库: {username}/{repo_name}")
    exists = check_github_repo_exists(username, repo_name)
    
    if exists:
        print("\n✅ 仓库存在，Streamlit部署问题可能是其他原因")
    else:
        print("\n❌ 仓库不存在，请检查仓库名称或创建仓库")
