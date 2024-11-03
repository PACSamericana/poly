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
            "retroperitoneum_peritoneum",
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
                        "normal": "Unremarkable.",
                        "subsections": {
                            "atelectasis": {
                                "normal": "No atelectasis.",
                                "options": [
                                    "Bibasilar dependent atelectasis.",
                                    "Right basilar atelectasis.",
                                    "Left basilar atelectasis.",
                                    "Areas of linear atelectasis vs. bandlike scarring in the right lung base.",
                                    "Areas of linear atelectasis vs. bandlike scarring in the left lung base.",
                                    "Multifocal areas of bandlike scarring versus atelectasis."
                                ]
                            },
                            "emphysema": {
                                "normal": "No emphysematous changes.",
                                "options": [
                                    "Mild upper lobe predominant centrilobular emphysema.",
                                    "Moderate upper lobe predominant centrilobular emphysema.",
                                    "Extensive centrilobular and paraseptal emphysema."
                                ]
                            },
                            "pleural": {
                                "normal": "No pleural effusion or pneumothorax.",
                                "options": [
                                    "Small right pleural effusion.",
                                    "Small left pleural effusion.",
                                    "Small bilateral pleural effusions."
                                ]
                            },
                            "fibrosis": {
                                "normal": "No fibrosis.",
                                "options": [
                                    "Basilar predominant subpleural reticulation, architectural distortion and traction bronchiectasis."
                                ]
                            }
                        }
                    },
                    "liver": {
                        "normal": "Normal size and attenuation. Smooth surface contour.",
                        "subsections": {
                            "appearance": {
                                "options": [
                                    "Mildly decreased attenuation",
                                    "Diffusely decreased attenuation",
                                    "Mildly nodular in contour",
                                    "Diffusely nodular in contour",
                                    "Enlarged measuring {size} cm in CC dimension at the midclavicular line and diffusely decreased in attenuation"
                                ]
                            },
                            "lesions": {
                                "normal": "No focal hepatic lesions.",
                                "options": [
                                    "Multiple peripheral hypervascular lesions in the right hepatic lobe some of which are likely hemangiomas and others of which may be perfusional-related changes, partially evaluated on this single phase exam.",
                                    "Hypervascular lesion in segment {location} measuring {size}mm with peripheral nodular enhancement and progressive fill-in on delayed phases."
                                ]
                            },
                            "cysts": {
                                "normal": "No hepatic cysts.",
                                "options": [
                                    "A few subcentimeter low-density foci too small to characterize, but likely benign.",
                                    "Scattered simple hepatic cysts measuring up to {size} mm.",
                                    "Simple cyst in the {location} hepatic lobe measuring {size} mm."
                                ]
                            },
                            "portal_vein": {
                                "normal": "Patent portal vein."
                            },
                            "trauma": {
                                "normal": "No evidence of hepatic injury.",
                                "options": [
                                    "Small laceration in the {location} lobe measuring {size}mm.",
                                    "Moderate laceration in the {location} lobe measuring {size}mm.",
                                    "Large laceration in the {location} lobe measuring {size}mm.",
                                    "Severe bilobar maceration.",
                                    "Complete hepatic avulsion.",
                                    "Small subcapsular hematoma in the {location} lobe measuring {size} mm.",
                                    "Small subcapsular or intraparenchymal hematoma in the {location} lobe measuring {size} mm.",
                                    "Moderate subcapsular or intraparenchymal hematoma in the {location} lobe measuring {size} mm.",
                                    "Large subcapsular or intraparenchymal hematoma in the {location} lobe measuring {size} mm.",
                                    "Complete parenchymal devascularization."
                                ]
                            }
                        }
                    },
                    "gallbladder_and_bile_ducts": {
                        "normal": "Normally-distended gallbladder, without radioopaque gallstones or associated inflammatory change. No biliary ductal dilation.",
                        "options": [
                            "Gallstones. No gallbladder wall thickening. No pericholecystic fluid. No biliary ductal dilation.",
                            "Surgically-absent. No biliary ductal dilatation.",
                            "Absent with mild biliary ductal dilation, likely related to post-cholecystectomy state.",
                            "Mild gallbladder wall thickening, likely due to third spacing.",
                            "Mild gallbladder wall thickening, nonspecific in the setting of underlying liver disease.",
                            "Contrast-filled gallbladder, likely due to vicarious-excretion.",
                            "Distended gallbladder containing radioopaque gallstones with wall thickening and pericholecystic fluid, consistent with acute cholecystitis.",
                            "Underdistended.",
                            "Moderately distended without radioopaque gallstones. No pericholecystic inflammatory changes.",
                            "Moderately distended containing sludge.",
                            "Contracted without radioopaque gallstones. No pericholecystic inflammatory changes."
                        ]
                    },
                    "pancreas": {
                        "normal": "Homogenously-enhancing without peripancreatic stranding or pancreatic lesion.",
                        "options": [
                            "Mildly atrophic.",
                            "Diffusely atrophic.",
                            "Atrophic with scattered coarse parenchymal calcifications.",
                            "Homogenously-enhancing with peripancreatic stranding. No necrosis or intrapancreatic collection. No pancreatic duct dilation. No mass.",
                            "{size} mm cystic lesion in the {location}. No main pancreatic ductal dilatation."
                        ]
                    },
                    "spleen": {
                        "normal": "Normal size and attenuation.",
                        "options": [
                            "Absent",
                            "Low density lesion measuring {size} mm, likely a cyst.",
                            "Low density lesion too small to characterize, but likely benign.",
                            "Mild splenomegaly.",
                            "Moderate splenomegaly.",
                            "Marked splenomegaly measuring {size} mm in length."
                        ]
                    },
                    "adrenal_glands": {
                        "normal": "Normal size and attenuation. No nodules.",
                        "options": [
                            "Mildly thickened bilaterally with no nodule.",
                            "Mild thickened right adrenal gland with no nodule. Normal left adrenal gland.",
                            "Mild thickened left adrenal gland with no nodule. Normal right adrenal gland.",
                            "Low-density right adrenal nodule measuring {size} mm. Normal left adrenal gland.",
                            "Low-density left adrenal nodule measuring {size} mm. Normal right adrenal gland.",
                            "Macroscopic fat-containing right adrenal nodule measuring {size} mm. Normal left adrenal gland.",
                            "Macroscopic fat-containing left adrenal nodule measuring {size} mm. Normal right adrenal gland."
                        ]
                    },
                    "kidneys_and_ureters": {
                        "normal": "Normal-sized kidneys with symmetric enhancement.",
                        "subsections": {
                            "appearance": {
                                "options": [
                                    "Unremarkable.",
                                    "Multifocal renal cortical scarring.",
                                    "Atrophic.",
                                    "Bilateral fetal lobulation."
                                ]
                            },
                            "stones": {
                                "normal": "No renal or ureteral calculi.",
                                "options": [
                                    "Nonobstructing stone in the {location} pole.",
                                    "Punctate nonobstructing {location} renal stones. No hydronephrosis.",
                                    "Punctate bilateral nonobstructing renal stones.",
                                    "Obstructing stone measuring {size} mm with {density} Hounsfield units of homogenous composition."
                                ]
                            },
                            "cysts": {
                                "options": [
                                    "Multiple subcentimeter low-density lesions, likely cysts.",
                                    "Multiple bilateral renal cysts and subcentimeter low-density lesions, likely representing additional cysts.",
                                    "Mild bilateral renal cortical thinning.",
                                    "Moderate bilateral renal cortical scarring.",
                                    "Mild bilateral renal cortical scarring. No renal or ureteral calculi. No hydronephrosis."
                                ]
                            },
                            "hydronephrosis": {
                                "normal": "No hydronephrosis.",
                                "options": [
                                    "Mild hydronephrosis.",
                                    "Moderate hydronephrosis.",
                                    "Severe hydronephrosis.",
                                    "Hydroureteronephrosis to the level of the {location} ureter."
                                ]
                            }
                        }
                    },
                    "urinary_bladder": {
                        "normal": "Normally-distended.",
                        "options": [
                            "Underdistended and circumferentially thickened.",
                            "Moderately distended.",
                            "Markedly distended.",
                            "Bladder diverticulum along the {location} bladder wall."
                        ]
                    },
                    "reproductive": {
                        "normal_female": "Normal uterus and adnexa.",
                        "normal_male": "Normal prostate gland and seminal vesicles.",
                        "options": [
                            "Absent uterus. No adnexal masses.",
                            "Small uterine fibroid measuring {size} mm.",
                            "A few small uterine fibroids measuring up to {size} mm.",
                            "Enlarged, myomatous uterus.",
                            "Mild prostatomegaly.",
                            "Moderate prostatomegaly.",
                            "Marked prostatomegaly with median lobe hypertrophy.",
                            "Surgically absent prostate.",
                            "TURP defect in the prostate.",
                            "Intrauterine device appropriately positioned within the endometrial cavity."
                        ]
                    },
                    "gastrointestinal": {
                        "normal": "Normally-distended bowel without abnormal wall thickening.",
                        "subsections": {
                            "stomach": {
                                "normal": "Normally-distended stomach.",
                                "options": [
                                    "Small hiatal hernia.",
                                    "Gastrostomy tube in appropriate position.",
                                    "Enteric tube terminating in the stomach.",
                                    "Feeding tube terminating in the duodenum.",
                                    "Incidental duodenal diverticulum.",
                                    "Status post Roux-en-Y gastric bypass.",
                                    "Underdistended stomach limiting evaluation.",
                                    "Partially-distended stomach."
                                ]
                            },
                            "bowel": {
                                "options": [
                                    "Normal appendix.",
                                    "Colonic diverticulosis without associated colonic wall thickening or surrounding stranding.",
                                    "Scattered colonic diverticula.",
                                    "Diffusely dilated loops of small bowel with transition point in the {location}.",
                                    "Diffusely dilated loops of small bowel with no transition point.",
                                    "Dilated appendix measuring {size} mm with/without a calcified appendicolith.",
                                    "Colonic diverticulosis with focal stranding surrounding a {location} colonic diverticulum with associated colonic wall thickening.",
                                    "Moderate amount of stool.",
                                    "Large amount of stool.",
                                    "Extensive predominantly left-sided colonic diverticulosis without associated colonic wall thickening or surrounding stranding.",
                                    "Surgically-absent appendix.",
                                    "Extensive predominantly left sided colonic diverticulosis with associated long segment sigmoid colonic wall thickening without surrounding stranding, likely representing sequelae of chronic diverticular disease."
                                ]
                            }
                        }
                    },
                    "retroperitoneum_peritoneum": {
                        "normal": "No free fluid, fluid collection, or free gas.",
                        "options": [
                            "Trace free fluid in the pelvis, likely physiologic.",
                            "Oval fat lobule with thin soft tissue rim-enhancement with adjacent fat stranding in the {location}.",
                            "{amount} volume ascites."
                        ]
                    },
                    "vessels": {
                        "normal": "No atherosclerotic calcifications.",
                        "subsections": {
                            "atherosclerosis": {
                                "options": [
                                    "Mild calcified aortic atherosclerosis.",
                                    "Mild multivessel calcified atherosclerosis.",
                                    "Moderate calcified aortic atherosclerosis.",
                                    "Moderate calcified atherosclerosis in the aorta and its branch vessels.",
                                    "Extensive calcified aortic atherosclerosis.",
                                    "Extensive calcified atherosclerosis in the aorta and its branch vessels."
                                ]
                            },
                            "aneurysm": {
                                "normal": "Normal aortic contour. No aneurysm.",
                                "options": [
                                    "Abdominal aortic aneurysm measuring {size} mm.",
                                    "Ectasia of the abdominal aorta measuring {size} mm."
                                ]
                            }
                        }
                    },
                    "lymph_nodes": {
                        "normal": "No enlarged lymph nodes.",
                        "options": [
                            "Small {location} nodes, not enlarged by CT size criteria and likely reactive.",
                            "Small retroperitoneal lymph nodes, not enlarged by CT size criteria and likely reactive."
                        ]
                    },
                    "abdominal_wall_soft_tissues": {
                        "normal": "Unremarkable.",
                        "options": [
                            "Postsurgical changes in the anterior abdominal wall.",
                            "Mild body wall edema.",
                            "Moderate body wall edema.",
                            "Severe body wall edema.",
                            "Small fat-containing right inguinal hernia.",
                            "Small fat-containing left inguinal hernia.",
                            "Small fat-containing umbilical hernia.",
                            "Incidental coarse calcifications in the gluteal subcutaneous soft tissues, likely dystrophic.",
                            "Small low-density foci in the abdominal wall likely represent sequelae of subcutaneous injections.",
                            "Rectus diastasis.",
                            "Small fat-containing inguinal hernias bilaterally."
                        ]
                    },
                      "bones": {
                        "normal": "No suspicious osseous lesions.",
                        "options": [
                            "Mild multilevel degenerative changes of the spine.",
                            "Bilateral chronic pars interarticularis fractures at {location}.",
                            "Intraosseous hemangioma at {location}.",
                            "Multiple scattered sclerotic foci, likely benign bone islands.",
                            "Moderate multilevel degenerative changes of the spine.",
                            "Severe multilevel degenerative changes of the spine.",
                            "No acute osseous abnormality."
                        ]
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
        
        prompt = f"""Please help me categorize these radiology findings into JSON format.
    
            Task: Take these raw findings and organize them by anatomical section.
    
            Raw findings: "{dictation}"
    
            STRICT RULES:
            1. Only include sections with EXPLICITLY mentioned findings
            2. Use EXACTLY the finding language provided - do not add details
            3. Return a valid JSON object
            4. Only use these exact section names:
                - lower_chest
                - liver
                - gallbladder_and_bile_ducts
                - pancreas
                - spleen
                - adrenal_glands
                - kidneys_and_ureters
                - urinary_bladder
                - reproductive
                - gastrointestinal
                - retroperitoneum_peritoneum
                - vessels
                - lymph_nodes
                - abdominal_wall_soft_tissues
                - bones
    
            Example input: "atelectasis, sigmoid diverticulitis"
            Example output:
            {{
                "lower_chest": "atelectasis",
                "gastrointestinal": "sigmoid diverticulitis"
            }}"""
    
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
        """Process a single section with strict adherence to input findings."""
        self.log_processing_step(f"SECTION: {section}", 
                               f"Processing with findings: {section_findings if section_findings else 'Using normal template'}")
        
        section_template = self.template["findings"]["sections"].get(section, {})
        normal_text = section_template.get("normal", "Normal examination.")
        
        if not section_findings:
            self.log_processing_step(f"SECTION: {section}", f"Using normal template text: {normal_text}")
            return {section: {"text": normal_text}}
    
        prompt = f"""Process this finding for the {section} section of a CT report.
    
            Finding: {section_findings}
    
            CRITICAL RULES:
            1. Output MUST contain ONLY information from the input text
            2. Use ONLY measurements EXPLICITLY stated in the input
            3. Preserve ALL image references (Series/Image numbers) exactly as given
            4. DO NOT create or infer ANY measurements
            5. DO NOT create or infer ANY image references
            6. DO NOT add ANY details not present in input
            7. DO NOT speculate or elaborate
            8. Format as a complete sentence with proper capitalization and ending period

            Return in this exact JSON format:
            {{
                "{section}": {{
                    "text": "Complete sentence with proper formatting and ALL original details."
                }}
            }}"""
            
        try:
            completion = await self.client.chat.completions.create(
                model="llama-3.2-3b-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise radiologist who reports findings as complete sentences, preserving ALL measurements and references while using proper capitalization and ending periods."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0,
                max_tokens=8192,
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

