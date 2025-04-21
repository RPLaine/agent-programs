from typing import Dict, Optional

class PromptManager:
    def __init__(self):
        self.templates: Dict[str, str] = {}
    
    def register_template(self, template_name: str, template_content: str) -> None:
        self.templates[template_name] = template_content
    
    def get_template(self, template_name: str) -> Optional[str]:
        return self.templates.get(template_name)
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        template = self.get_template(template_name)
        if template is None:
            raise KeyError(f"Prompt template not found: {template_name}")
        
        return template.format(**kwargs)
    
    def register_templates_from_module(self, module) -> None:
        for name, value in module.__dict__.items():
            if name.endswith('_PROMPT') and isinstance(value, str):
                self.register_template(name, value)
