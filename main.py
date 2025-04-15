import os
import sys
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utility.job_manager import Job, JobManager
from utility.file_handler import FileHandler
from utility.tool_manager import ToolManager
from utility.user_interaction import UserInteraction

class DolphinAI:
    def __init__(self):
        self.job_manager = JobManager()
        self.file_handler = FileHandler(base_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "files"))
        self.tool_manager = ToolManager()
        self.user_interaction = UserInteraction()
        self.output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        
        os.makedirs(self.output_dir, exist_ok=True)
    
    def initialize(self):
        print("Initializing Dolphin AI...")
        self.tool_manager.discover_tools()
        print(f"Found {len(self.tool_manager.available_tools)} tools")
        print("Dolphin AI ready to accept jobs")
        
    def create_job(self, description: str) -> Optional[str]:
        try:
            job_id = self.job_manager.create_job(description)
            print(f"Created job: {job_id}")
            
            job = self.job_manager.get_job(job_id)
            if job is None:
                print(f"Error: Job {job_id} not found immediately after creation")
                return None
            
            job.update_status("Analyzing")
            self.begin_job(job)
            return job_id
        except Exception as e:
            print(f"Error creating job: {str(e)}")
            return None
    
    def begin_job(self, job: Job):
        print(f"\nStarting job: {job.description}")
        job.status = "In Progress"
        
        required_info = self.analyze_job_requirements(job)
        if required_info:
            job.status = "Awaiting User Input"
            user_input = self.user_interaction.request_information(required_info)
            job.add_context({"user_input": user_input})
        
        job.status = "Working"
        result = self.execute_job(job)
        
        if result:
            job.status = "Completed"
            print(f"\nJob completed: {job.id}")
            print(f"Results saved to: {result}")
        else:
            job.status = "Failed"
            print(f"\nJob failed: {job.id}")
    
    def analyze_job_requirements(self, job: Job) -> List[str]:
        print(f"Analyzing requirements for job: {job.description}")
        
        analysis_tool = self.tool_manager.get_tool("information_distiller")
        if analysis_tool:
            extracted_info = analysis_tool.extract_key_information(job.description)
            job.add_context({"analysis": extracted_info})
            
            required_info = []
            if "?" in job.description:
                required_info.append("Please provide more details about your question.")
            
            return required_info
        
        return []
    
    def execute_job(self, job: Job) -> str:
        print(f"Executing job: {job.description}")
        
        if self.is_information_gathering(job):
            return self.gather_information(job)
        else:
            return self.create_product(job)
    
    def is_information_gathering(self, job: Job) -> bool:
        text = job.description.lower()
        info_keywords = ["find", "search", "look up", "research", "gather", "collect", "information", "data"]
        
        return any(keyword in text for keyword in info_keywords)
    
    def gather_information(self, job: Job) -> str:
        print("Gathering information...")
        
        if self.needs_web_research(job):
            web_research_tool = self.tool_manager.get_tool("utils.web_research")
            if web_research_tool:
                research = web_research_tool.get_web_research(job.description)
                job.add_context({"web_research": research})
        
        summarize_tool = self.tool_manager.get_tool("summarization")
        if summarize_tool and "web_research" in job.context:
            summary = summarize_tool.summarization(job.context["web_research"]["summary"])
            job.add_context({"summary": summary})
        
        output_file = os.path.join(self.output_dir, f"{job.id}_results.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Job: {job.description}\n\n")
            if "summary" in job.context:
                f.write(f"Summary:\n{job.context['summary']}\n\n")
            if "web_research" in job.context:
                f.write(f"Sources:\n")
                for link in job.context["web_research"]["links"]:
                    f.write(f"- {link}\n")
        
        return output_file
    
    def create_product(self, job: Job) -> str:
        print("Creating product...")
        
        output_file = os.path.join(self.output_dir, f"{job.id}_product.txt")
        
        content = self.generate_content(job)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        return output_file
    
    def generate_content(self, job: Job) -> str:
        content = f"Generated content for: {job.description}\n\n"
        
        text_processor = self.tool_manager.get_tool("text_processor")
        if text_processor:
            processed_content = text_processor.process_text(
                job.description, 
                extraction_goal="Generate content based on the job description"
            )
            content += processed_content["final_output"]
        else:
            content += f"This is a placeholder for generated content related to: {job.description}"
        
        return content
    
    def needs_web_research(self, job: Job) -> bool:
        text = job.description.lower()
        web_keywords = ["internet", "web", "online", "search", "find", "research"]
        
        return any(keyword in text for keyword in web_keywords)
    
    def status_report(self, job_id: str = ""):
        if job_id:
            job = self.job_manager.get_job(job_id)
            if job:
                print(f"\nJob Status Report: {job.id}")
                print(f"Description: {job.description}")
                print(f"Status: {job.status}")
                print(f"Created: {job.created_at}")
                print(f"Last Updated: {job.updated_at}")
                return
            else:
                print(f"Job not found: {job_id}")
        
        jobs = self.job_manager.list_jobs()
        print("\nAll Jobs Status Report:")
        for job_id, job in jobs.items():
            print(f"- Job {job.id}: {job.status} - {job.description[:50]}...")


def main():
    ai = DolphinAI()
    ai.initialize()
    
    while True:
        print("\n" + "="*50)
        print("Dolphin AI - Your AI Assistant")
        print("="*50)
        print("1. Create a new job")
        print("2. Get status report")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            description = input("\nPlease describe the job: ")
            ai.create_job(description)
        elif choice == "2":
            job_id = input("\nEnter job ID (leave empty for all jobs): ")
            ai.status_report(job_id if job_id else "")        
        elif choice == "3":
            print("\nExiting Dolphin AI. Goodbye!")
            break
        else:
            print(f"\nInvalid choice '{choice}'. Please enter 1, 2, or 3 to select from the menu options.")


if __name__ == "__main__":
    main()
