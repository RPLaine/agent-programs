import time
import uuid
from typing import Dict, Any, Optional


class Job:
    def __init__(self, job_id: str, description: str):
        self.id = job_id
        self.description = description
        self.status = "Created"
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
        self.context = {}
    
    def update_status(self, status: str):
        self.status = status
        self.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
    
    def add_context(self, new_context: Dict[str, Any]):
        self.context.update(new_context)
        self.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")


class JobManager:
    def __init__(self):
        self.jobs = {}
    
    def create_job(self, description: str) -> str:
        job_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for simplicity
        self.jobs[job_id] = Job(job_id, description)
        return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)
    
    def update_job_status(self, job_id: str, status: str) -> bool:
        if job_id in self.jobs:
            self.jobs[job_id].update_status(status)
            return True
        return False
    
    def list_jobs(self) -> Dict[str, Job]:
        return self.jobs
