#!/usr/bin/env python3
"""Meeting check script for cron - checks all meetings and reports.
Checks for:
1. Meetings that need input (running, waiting for submissions)
2. Completed meetings (all submitted) that need finalization (>2 hours old)
3. Flag meetings that need follow-up discussion
"""
import os
import sys
import requests
from datetime import datetime, timedelta
import json

API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")

def get_meetings():
    r = requests.get(f"{API_BASE}/meetings", timeout=15)
    r.raise_for_status()
    return r.json() or []

def get_meeting_detail(mid):
    r = requests.get(f"{API_BASE}/meetings/{mid}", timeout=15)
    r.raise_for_status()
    return r.json()

def check_meetings():
    meetings = get_meetings()
    
    if not meetings:
        print("No meetings found.")
        return
    
    print("=" * 60)
    print("MEETING STATUS REPORT")
    print("=" * 60)
    
    needs_finalization = []
    
    for m in meetings:
        mid = m.get("id")
        topic = m.get("topic", "")
        status = m.get("status", "")
        created_at = m.get("created_at", "")
        
        detail = get_meeting_detail(mid)
        participants = detail.get("participants", [])
        submitted = len([p for p in participants if p.get("status") == "submitted"])
        
        all_submitted = submitted == len(participants) and len(participants) > 0
        
        is_old = False
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                now = datetime.now(dt.tzinfo)
                is_old = (now - dt) > timedelta(hours=2)
            except:
                pass
        
        print(f"\n📌 Meeting {mid}: {topic}")
        print(f"   Status: {status}")
        print(f"   Submitted: {submitted}/{len(participants)}")
        
        # Finalize if: all submitted + >2h OR any submission + >8h (even if incomplete)
        if status == "running" and is_old and (all_submitted or submitted > 0):
            print(f"   ⚠️  NEEDS FINALIZATION! (>2h old, {submitted} submissions)")
            needs_finalization.append(mid)
        elif status == "running" and all_submitted:
            print(f"   📝 All submitted, waiting...")
        elif status == "running":
            print(f"   ⏳ In progress...")
        
        if status == "concluded":
            print(f"   ✅ Completed")
    
    print("\n" + "=" * 60)
    
    if needs_finalization:
        print(f"⚠️  MEETINGS NEEDING FINALIZATION: {needs_finalization}")
        print("To finalize: POST to /api/meetings/<id>/finalize with conclusion_summary and conclusion_decision")
        print("To continue discussion: Create new meeting with same topic + '_续' or '_follow-up'")
    
    return needs_finalization

def check_and_suggest_followup():
    """Check concluded meetings and suggest if follow-up is needed."""
    meetings = get_meetings()
    
    print("=" * 60)
    print("CONCLUDED MEETINGS - CHECK FOR FOLLOW-UP")
    print("=" * 60)
    
    for m in meetings:
        if m.get("status") != "concluded":
            continue
            
        mid = m.get("id")
        topic = m.get("topic", "")
        conclusion = m.get("conclusion_summary", "") or ""
        decision = m.get("conclusion_decision", "") or ""
        
        # Keywords that suggest more analysis might be needed
        followup_keywords = ["待续", "继续", "进一步", "后续", "monitor", "follow-up", "continue", "进一步分析"]
        needs_followup = any(kw in conclusion or kw in decision for kw in followup_keywords)
        
        print(f"\n📌 Meeting {mid}: {topic}")
        if needs_followup:
            print(f"   🔄 SUGGESTED: Continue discussion")
            print(f"   Conclusion: {conclusion[:100]}...")
        else:
            print(f"   ✅ Concluded")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--followup":
        check_and_suggest_followup()
    else:
        check_meetings()
