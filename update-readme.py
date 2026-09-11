#!/usr/bin/env python3
"""
Script to automatically update GitHub README with latest stats
Updates: Latest Repositories, Last Update Time
"""

import os
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration - यहाँ USERNAME दो
GITHUB_USERNAME = "deepakkr62040"      # 👈 अपना username डालो
LEETCODE_USERNAME = "Deepakkr62040"    # 👈 अपना LeetCode username डालो
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Headers for API requests
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "User-Agent": "ReadmeUpdater"
}

def get_github_repos():
    """Fetch latest GitHub repositories with stars"""
    try:
        url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
        params = {
            "sort": "updated",
            "order": "desc",
            "per_page": 10
        }
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        repos = response.json()
        
        repos_data = []
        for repo in repos[:3]:  # Top 3 repos
            repos_data.append({
                "name": repo["name"],
                "url": repo["html_url"],
                "stars": repo["stargazers_count"],
                "language": repo["language"] or "Unknown",
                "description": repo["description"] or "No description",
                "updated_at": repo["updated_at"]
            })
        
        return repos_data
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

def get_leetcode_stats():
    """Fetch LeetCode statistics"""
    try:
        url = f"https://leetcode.com/graphql"
        
        query = {
            "query": """
            {
                matchedUser(username: "%s") {
                    username
                    profile {
                        realName
                        userAvatar
                    }
                    submitStatsGlobal {
                        acSubmissionNum {
                            difficulty
                            count
                            submissions
                        }
                    }
                }
            }
            """ % LEETCODE_USERNAME
        }
        
        response = requests.post(url, json=query, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("data", {}).get("matchedUser"):
            user = data["data"]["matchedUser"]
            stats = user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
            
            total_solved = 0
            for stat in stats:
                if stat.get("difficulty") == "All":
                    total_solved = stat.get("count", 0)
            
            return {
                "username": user.get("username"),
                "total_solved": total_solved
            }
        return None
    except Exception as e:
        print(f"Error fetching LeetCode stats: {e}")
        return None

def update_readme_section(content, marker_start, marker_end, new_content):
    """Update a specific section in README between markers"""
    pattern = f"<!-- {marker_start} -->.*?<!-- {marker_end} -->"
    replacement = f"<!-- {marker_start} -->\n{new_content}\n<!-- {marker_end} -->"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def format_repos_table(repos):
    """Format repositories as a markdown table"""
    table = "| Repository | Stars | Language | Last Updated |\n"
    table += "|-----------|-------|----------|---------------|\n"
    
    for repo in repos:
        date = repo["updated_at"].split("T")[0]
        stars = "⭐" * min(repo["stars"], 5) if repo["stars"] > 0 else "✨"
        
        table += f"| [{repo['name']}]({repo['url']}) | {stars} | {repo['language']} | {date} |\n"
    
    return table

def get_timestamp():
    """Get current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

def main():
    """Main function to update README"""
    print("🤖 Starting README update...")
    
    # Read current README
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print("❌ README.md not found!")
        return
    
    # Fetch data
    print("📊 Fetching GitHub stats...")
    
    print("📚 Fetching repositories...")
    repos = get_github_repos()
    
    print("🏆 Fetching LeetCode stats...")
    leetcode_stats = get_leetcode_stats()
    
    # Generate updated sections
    repos_table = format_repos_table(repos) if repos else "No repositories found."
    timestamp = get_timestamp()
    
    # Update README content
    print("✏️ Updating README sections...")
    
    # Update repos section
    readme_content = update_readme_section(
        readme_content,
        "LATEST_REPOS:START",
        "LATEST_REPOS:END",
        f"**📌 Recent Repositories (Auto-Updated Daily)**\n\n{repos_table}"
    )
    
    # Update timestamp
    readme_content = re.sub(
        r"<!-- LAST_UPDATED -->.*?<!-- LAST_UPDATED_END -->",
        f"<!-- LAST_UPDATED -->{timestamp}<!-- LAST_UPDATED_END -->",
        readme_content,
        flags=re.DOTALL
    )
    
    # Write updated README
    print("💾 Writing updated README...")
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README updated successfully!")
    print(f"   • Repositories: {len(repos)}")
    print(f"   • Last Update: {timestamp}")
    if leetcode_stats:
        print(f"   • LeetCode Problems Solved: {leetcode_stats['total_solved']}")

if __name__ == "__main__":
    main()
