import streamlit as st
import json
from groq import AsyncGroq
from typing import Dict, Any
import os
from datetime import datetime
import asyncio

class CTReportGenerator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
            
        self.client = AsyncGroq(api_key=self.api_key)
            
        self.sections = [
            "lower_chest",
            "liver",
            "gallbladder_and_bile_ducts",
            "pancreas",
            "spleen",
            "adrenal_glands",
            "kidneys_and_ureters",
            "urinary_bladder",
            "reproductive",
            "gastrointestinal",
            "peritoneum",
            "vessels",
            "lymph_nodes",
            "abdominal_wall_soft_tissues",
            "bones"
        ]

        self.template = {
            "study_type": "CT Abdomen and Pelvis",
            "findings": {
                "sections": {
                    "lower_chest": {
                        "normal": "The visualized lower lungs are clear without focal consolidation, pleural effusion, or pneumothorax."
                    },
                    "liver": {
                        "normal": "Normal size and attenuation with smooth surface contour. No focal hepatic lesions. Portal and hepatic veins are patent."
                    },
                    "gallbladder_and_bile_ducts": {
                        "normal": "Normally-distended gallbladder without gallstones or wall thickening. No biliary ductal dilation."
                    },
                    "pancreas": {
                        "normal": "Normal-appearing pancreas without mass, ductal dilation, or peripancreatic fluid."
                    },
                    "spleen": {
                        "normal": "Normal-sized spleen without focal lesion."
                    },
                    "adrenal_glands": {
                        "normal": "Normal-appearing adrenal glands without nodule or mass."
                    },
                    "kidneys_and_ureters": {
                        "normal": "Normal-sized kidneys with symmetric enhancement. No hydronephrosis or renal stones."
                    },
                    "urinary_bladder": {
                        "normal": "Normal-appearing urinary bladder without wall thickening or mass."
                    },
                    "reproductive": {
                        "normal": "Reproductive organs are unremarkable."
                    },
                    "gastrointestinal": {
                        "normal": "No bowel wall thickening. Small and large bowel are normal in caliber. Normal-appearing appendix."
                    },
                    "peritoneum": {
                        "normal": "No free intraperitoneal air or fluid."
                    },
                    "vessels": {
                        "normal": "Normal caliber abdominal aorta and major branch vessels without significant atherosclerotic disease."
                    },
                    "lymph_nodes": {
                        "normal": "No abnormally enlarged lymph nodes."
                    },
                    "abdominal_wall_soft_tissues": {
                        "normal": "Normal-appearing abdominal wall without hernia or mass."
                    },
                    "bones": {
                        "normal": "No suspicious osseous lesion. Age-appropriate degenerative changes."
                    }
                }
            }
        }

    def log_processing_step(self, step: str, message: str):
        """Utility function to log processing steps"""
        st.text(f"[{step}] {message}")

    async def categorize_findings(self, dictation: str) -> Dict[str, str]:
        """Preprocessing step to categorize findings."""
        self.log_processing_step("PREPROCESS", f"Input dictation: {dictation}")
        
        prompt = f"""You are a radiologist assistant categorizing imaging findings.
    
        TASK: Analyze this dictation and assign each finding to EXACTLY ONE most appropriate anatomical section.
    
        Raw dictation: "{dictation}"
    
        CRITICAL RULES:
        1. EVERY finding MUST be categorized
        2. Each finding goes to ONE section only
        3. Lung findings (atelectasis, effusion, etc.) ALWAYS go to lower_chest
        4. Related findings MUST stay together (e.g., appendix and surrounding changes go together in gastrointestinal)
        5. Preserve exact measurements and image references with their findings
        6. Use these exact section names: {json.dumps(self.sections, indent=2)}
    
        Output format:
        {{
            "section_name": [
                {{
                    "finding": "exact finding text",
                    "series": "Series X if present",
                    "image": "Image Y if present"
                }}
            ]
        }}
    
        Remember:
        - NEVER split related findings across sections
        - NEVER skip any finding
        - ALL lung findings go to lower_chest
        
        Return a JSON object mapping sections to their findings, preserving exact wording."""

    # Rest of your method remains the same
    
    # Rest of your method remains the same
    
        try:
            completion = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Changed to more powerful model
                messages=[
                    {"role": "system", "content": "You are a radiologist assistant that categorizes findings by anatomical section. Maintain all reference information like image numbers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=8000,
                top_p=0.1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None
            )
            
            categorized = json.loads(completion.choices[0].message.content)
            self.log_processing_step("PREPROCESS", f"Categorized findings: {json.dumps(categorized, indent=2)}")
            return categorized
            
        except Exception as e:
            self.log_processing_step("ERROR", f"Preprocessing error: {str(e)}")
            return {}
    
    async def process_section(self, section: str, section_findings: str = None) -> Dict[str, Any]:
        """Process a single section by intelligently integrating findings into the normal template."""
        self.log_processing_step(f"SECTION: {section}", 
                               f"Processing with findings: {section_findings if section_findings else 'Using normal template'}")
        
        section_template = self.template["findings"]["sections"].get(section, {})
        normal_text = section_template.get("normal", "Normal examination.")
        
        if not section_findings:
            self.log_processing_step(f"SECTION: {section}", f"Using normal template text: {normal_text}")
            return {section: {"text": normal_text}}
    
        prompt = f"""Process this finding for the {section} section of a CT report.
    
            Normal Template: "{normal_text}"
            Finding to integrate: "{section_findings}"
    
            CRITICAL RULES:
            1. NEVER say "normal" or "normal-appearing" for any structure that has an abnormality
            2. Start by identifying what parts of the normal template are contradicted by the findings
            3. Replace contradicted parts while keeping unaffected parts
            4. Each finding object has:
               - "finding": the actual finding text
               - "series": series reference if present
               - "image": image reference if present
            6. When including a finding that has series/image references, 
               add them in parentheses at the end of that finding like:
               "...shows mass (Series 2 Image 45)"
            7. Create natural sentence flow
    
            Examples:
            Finding: "mild fatty atrophy pancreas"
            BAD: "Normal-appearing pancreas with mild fatty atrophy" (contradiction)
            GOOD: "Pancreas demonstrates mild fatty atrophy. No mass or ductal dilation."
    
            Finding: "periappendiceal fat stranding with 6mm appendicolith"
            BAD: "Normal-appearing appendix with periappendiceal fat stranding" (contradiction)
            GOOD: "Appendix shows periappendiceal fat stranding with a 6mm appendicolith"
    
            Return in this exact JSON format:
            {{
                "{section}": {{
                    "text": "Complete sentence(s) integrating findings correctly."
                }}
            }}"""
            
        try:
            completion = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise radiologist who intelligently integrates findings into normal templates while maintaining accuracy and natural language flow."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0,
                max_tokens=8000,
                top_p=0.1,
                stream=False,
                response_format={"type": "json_object"},
                stop=None
            )
            
            result = json.loads(completion.choices[0].message.content)
            self.log_processing_step(f"SECTION: {section}", f"Generated text: {result[section]['text']}")
            return result
            
        except Exception as e:
            self.log_processing_step("ERROR", f"Error processing {section}: {str(e)}")
            return {section: {"text": normal_text}}

    def convert_to_text_report(self, report_json: Dict[str, Any]) -> str:
        """Convert JSON report to markdown formatted text."""
        text_report = []
        text_report.append("# CT ABDOMEN AND PELVIS REPORT")
        text_report.append("\n## FINDINGS:")
        
        sections = report_json.get("findings", {}).get("sections", {})
        for section in self.sections:
            if section in sections:
                section_name = section.replace("_", " ").title()
                section_text = sections[section]["text"]
                text_report.append(f"\n### {section_name}")
                text_report.append(f"{section_text}")
        
        return "\n".join(text_report)

    async def generate_report(self, dictation: str) -> Dict[str, Any]:
        """Generate complete report with logging."""
        self.log_processing_step("START", "Beginning report generation")
        
        # First, categorize findings
        categorized_findings = await self.categorize_findings(dictation)
        
        # Process each section
        report = {"findings": {"sections": {}}}
        for section in self.sections:
            section_findings = categorized_findings.get(section)
            result = await self.process_section(section, section_findings)
            if result:
                report["findings"]["sections"].update(result)
        
        self.log_processing_step("COMPLETE", "Report generation finished")
        return report

# Modify the Streamlit interface part:
st.title('CT Report Generator')

dictation = st.text_area(
    "Enter dictation:",
    placeholder="Example: mild steatosis, 5mm distal right ureter stone...",
    height=100
)

if st.button('Generate Report'):
    if dictation:
        try:
            st.subheader("Processing Log:")
            generator = CTReportGenerator()
            report = asyncio.run(generator.generate_report(dictation))
            
            # Display formatted markdown report
            st.subheader("Generated Report:")
            text_report = generator.convert_to_text_report(report)
            st.markdown(text_report)  # Changed from st.text() to st.markdown()
            
            # Save the JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ct_report_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            st.success(f"Report saved as {filename}")
            
            # Show raw JSON if needed
            if st.checkbox("Show raw JSON"):
                st.json(report)
                
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
    else:
        st.error("Please enter dictation text.")

