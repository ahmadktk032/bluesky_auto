"""
Bluesky Setup Helper
Creates configuration and schedule files
"""

import json
from datetime import datetime, timedelta


def create_schedule(start_date="2025-12-09", days=7):
    """Create 7-day schedule with sample topics"""
    
    topics = [
        # Day 1
        ["Why decentralized social media matters", 
         "5 things I learned building in public",
         "The future of online communities"],
        # Day 2
        ["How I grew my following from 0 to 1000",
         "Common mistakes in content creation",
         "Building authentic connections online"],
        # Day 3
        ["My journey learning to code at 30",
         "Productivity systems that actually work",
         "Why consistency beats perfection"],
        # Day 4
        ["The art of writing engaging threads",
         "How to find your unique voice online",
         "Lessons from 100 days of posting"],
        # Day 5
        ["Understanding web3 and decentralization",
         "My biggest failure and what I learned",
         "How to overcome creative blocks"],
        # Day 6
        ["Building a sustainable side hustle",
         "The power of community over followers",
         "Why I left Twitter for Bluesky"],
        # Day 7
        ["Tools I use for content creation",
         "How to manage time as a creator",
         "My content strategy for 2025"]
    ]
    
    schedule = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    times = ["09:00", "14:00", "19:00"]
    
    for day in range(1, days + 1):
        date = start + timedelta(days=day - 1)
        day_topics = topics[(day - 1) % len(topics)]
        
        threads = []
        for idx, time in enumerate(times):
            threads.append({
                "time": time,
                "topic": day_topics[idx],
                "image": None  # Set to image path if you have images
            })
        
        schedule.append({
            "day": day,
            "date": date.strftime("%Y-%m-%d"),
            "threads": threads
        })
    
    return schedule


def save_for_github_secret(schedule):
    """Save schedule for GitHub Secret"""
    filename = "BLUESKY_SCHEDULE.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Schedule saved: {filename}")
    print(f"\nSchedule info:")
    print(f"  Days: {len(schedule)}")
    print(f"  Total threads: {len(schedule) * 3}")
    print(f"  Date range: {schedule[0]['date']} to {schedule[-1]['date']}")
    
    print(f"\n{'='*70}")
    print("TO ADD TO GITHUB SECRET:")
    print("="*70)
    print(f"1. Open {filename}")
    print("2. Copy ALL content (Ctrl+A, Ctrl+C)")
    print("3. GitHub → Settings → Secrets → Actions")
    print("4. New secret: BLUESKY_SCHEDULE")
    print("5. Paste and save")
    print("="*70)


def save_local_config(schedule):
    """Save complete local config"""
    config = {
        "_comment": "Bluesky Automation Configuration",
        
        "ai_providers": {
            "groq": "your-groq-api-key-here",
            "gemini": "your-gemini-api-key-here"
        },
        
        "bluesky": {
            "handle": "username.bsky.social",
            "app_password": "xxxx-xxxx-xxxx-xxxx"
        },
        
        "posting_times": ["09:00", "14:00", "19:00"],
        "schedule": schedule
    }
    
    with open('bluesky_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Local config saved: bluesky_config.json")
    print("\nEdit this file:")
    print("  1. Add your Groq/Gemini API keys")
    print("  2. Add your Bluesky handle")
    print("  3. Add your Bluesky app password")
    print("  4. Customize topics if desired")


if __name__ == '__main__':
    print("="*70)
    print("BLUESKY AUTOMATION SETUP")
    print("="*70 + "\n")
    
    # Create schedule
    schedule = create_schedule(start_date="2025-12-09", days=7)
    
    # Show preview
    print("Schedule preview:")
    for day in schedule[:2]:
        print(f"\nDay {day['day']} ({day['date']}):")
        for thread in day['threads']:
            print(f"  {thread['time']}: {thread['topic']}")
    print("  ... (5 more days)")
    print()
    
    # Save files
    save_for_github_secret(schedule)
    save_local_config(schedule)
    
    print("\n" + "="*70)
    print("SETUP COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Edit bluesky_config.json with your credentials")
    print("2. Test locally: python bluesky_automation.py preview")
    print("3. Copy BLUESKY_SCHEDULE.json to GitHub Secret")
    print("="*70)