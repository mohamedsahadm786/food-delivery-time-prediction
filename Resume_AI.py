# file: your_module.py

import os
import json
import subprocess
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import openai

# ========== CONFIG ==========
client = openai.OpenAI(api_key="Your_GPT_API_Key")

TEX_TEMPLATE_RESUME = "resume_template.tex"
TEX_TEMPLATE_COVER = "cover_letter_template.tex"
PROJECTS_JSON_PATH = "projects.json"
PROFILE_TXT_PATH = "profile.txt"
DEFAULT_SECTIONS_JSON = "default_sections.json"
ENRICHED_SECTIONS_JSON = "default_sections.enriched.json"
JSON_SECTIONS_COVER_LETTER = "cover_letter_sections.json"
OUTPUT_TEX = "output/resume_generated.tex"
OUTPUT_PDF = "output/resume_generated.pdf"
TEX_OUTPUT_PATH = "resume_filled.tex"

LATEX_ENV = Environment(
    block_start_string='((*',
    block_end_string='*))',
    variable_start_string='(((',
    variable_end_string=')))',
    comment_start_string='((=',
    comment_end_string='=))',
    loader=FileSystemLoader('.')
)

# ========== UTILS ==========
def escape_latex(text):
    replacements = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\^{}',
        '\\': r'\textbackslash{}'
    }
    pattern = re.compile('|'.join(re.escape(k) for k in replacements))
    return pattern.sub(lambda m: replacements[m.group()], text)


def strip_markdown_fences(text: str) -> str:
    if text.startswith("```"):
        return text.strip("`").split("\n", 1)[-1].rsplit("\n", 1)[0].strip()
    return text.strip()

def strip_markdown(text: str) -> str:
    """
    Removes triple backtick blocks (e.g. ```latex ... ```) from GPT output.
    """
    lines = text.strip().splitlines()
    lines = [line for line in lines if not line.strip().startswith("```")]
    return "\n".join(lines).strip()


def extract_section_keys(json_path: str) -> list:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return list(data.keys())

def run_latex(tex_file, output_dir):
    subprocess.run([
        "pdflatex", f"-output-directory={output_dir}", tex_file
    ], check=True)

# ========== FUNCTION 1: SELECT PROJECTS ==========
def select_best_projects(
    projects: dict, 
    job_title: str, 
    company_name: str, 
    job_description: str, 
    location: str = None
):
    # Ensure all projects have 'latex_block'
    for key, proj in projects.items():
        if 'latex_block' not in proj:
            raise KeyError(f"Project '{key}' missing 'latex_block'")

    prompt = f"""
Mohamed Sahad is applying for the job below.

--- JOB INPUT ---
- Job Title: {job_title}
- Company: {company_name}
- Location: {location or 'Not specified'}
- Job Description:
{job_description}

--- CANDIDATE PROJECTS ---
You are given 8 LaTeX-formatted projects tagged with keys like "PROJECTS_ESG", "PROJECTS_AMAZON", etc.

--- YOUR TASK ---
Select **exactly 4 unique projects** from this set that are the most strategically relevant to the job based on the job title and job description above.

--- SELECTION CRITERIA (MUST FOLLOW STRICTLY) ---

1. **Relevance First**: Choose projects that demonstrate **direct alignment** with the job’s required skills, tools, methods, domain, or deliverables. Examples of such alignment include:
   - Overlapping technologies (e.g., Python, SQL, ML, DL, NLP, LLMs, data visualization tools)
   - Domain similarity (e.g., finance, healthcare, e-commerce, sustainability)
   - Shared focus (e.g., modeling, automation, analytics, prediction, optimization, deployment)

2. **No Keyword Matching**: Do not rely on surface-level keyword matches. Analyze the job description deeply to understand what problems the company is solving and which project contributions reflect the right skills.

3. **Exclude Weak Matches**: Do **not include projects** that are:
   - Outdated or using non-relevant tech stacks (e.g., SAS for non-healthcare jobs)
   - Focused only on BI/dashboards unless the job emphasizes analytics or reporting
   - Lacking ML, DL, or coding if the job requires model development or technical skills

4. **Maximize Strategic Fit**:
   - Pick projects that showcase transferable skills, measurable outcomes, or innovation.
   - Prefer end-to-end projects (problem framing → data processing → modeling → output).
   - Favor projects that show autonomy, practical utility, or deployment-readiness.

5. **Avoid Redundancy**:
   - Do not choose multiple projects that reflect the same skill unless it is a core focus of the job (e.g., multiple deep learning projects only if the job emphasizes DL).
   - Ensure each of the 4 selected projects **adds unique value** to Mohamed’s profile for that specific job.

6. **Think Like a Hiring Manager**:
   - Imagine you are shortlisting Mohamed for this job.
   - Only include projects that make his profile stronger for this specific role and company.
   - The goal is **not variety for variety's sake**, but to **optimize Mohamed's chances** of getting noticed and interviewed.

--- OUTPUT FORMAT ---
Return a JSON list of only the selected 4 project keys, ordered by descending relevance.
Example:
["PROJECTS_CLINICAL", "PROJECTS_ESG", "PROJECTS_AMAZON", "PROJECTS_CHATBOT"]

DO NOT return any explanation, LaTeX, markdown, or text – ONLY the list of 4 keys as a raw JSON array.
""".strip()


    latex_snippets = "\n\n".join(
        f"[{key}]\n{proj['latex_block']}" 
        for key, proj in projects.items()
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You're an expert resume optimizer. Return ONLY a JSON array of 4 project keys. No markdown, no text, no LaTeX."
                )
            },
            {"role": "user", "content": f"{prompt}\n\n{latex_snippets}"}
        ]
    )

    raw_output = response.choices[0].message.content.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`").split("\n", 1)[-1].rsplit("\n", 1)[0].strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        raise ValueError("\u274c GPT output not parseable as JSON. Raw output:\n" + raw_output)





# ========== FUNCTION 2: INJECT PROJECTS INTO TEMPLATE ==========
def inject_projects_into_template(template_path: str, output_path: str, selected_keys: list[str], projects: dict[str, dict[str, str]]):
    # Load LaTeX template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Iterate over 4 selected project keys and replace placeholders
    for i, project_key in enumerate(selected_keys):
        placeholder = f"((( PROJECT_BLOCK_{i + 1} )))"
        latex_block = projects[project_key]["latex_block"].strip()
        template = template.replace(placeholder, latex_block)

    # Remove any remaining unused placeholders just in case
    for i in range(len(selected_keys), 4):
        template = template.replace(f"((( PROJECT_BLOCK_{i + 1} )))", "")

    # Save filled template
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)




# ========== FUNCTION 3: BUILD ENRICHED SECTIONS ==========
def build_enriched_sections(base_path: str, enriched_path: str, selected_keys: list[str], projects: dict[str, dict[str, str]]):
    with open(base_path, 'r', encoding='utf-8') as f:
        sections = json.load(f)

    for key in selected_keys:
        bullets = projects[key].get("bullets", "").strip()
        sections[key] = bullets

    with open(enriched_path, 'w', encoding='utf-8') as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)

        

# ========== FUNCTION 2: GENERATE RESUME (MODULAR) ==========
def prompt_gpt4o(job_title, company_name, location, job_description, output_dir):
    # Load full 7-projects data
    with open(PROJECTS_JSON_PATH, "r", encoding="utf-8") as f:
        all_projects = json.load(f)

    # 🔮 Dynamically choose best 4
    selected_keys = select_best_projects(all_projects, job_title, company_name, job_description, location)

    inject_projects_into_template(
        template_path=TEX_TEMPLATE_RESUME,
        output_path=TEX_OUTPUT_PATH,
        selected_keys=selected_keys,
        projects=all_projects  # this should be your full project dictionary
    )  # This will generate resume_filled.tex

    build_enriched_sections(
        base_path=DEFAULT_SECTIONS_JSON,
        enriched_path=ENRICHED_SECTIONS_JSON,
        selected_keys=selected_keys,
        projects=all_projects
    )

        # Load user's real background from profile.txt
    with open(PROFILE_TXT_PATH, "r", encoding="utf-8") as f:
        PERSONAL_PROFILE = f.read().strip()

    template = LATEX_ENV.get_template(TEX_OUTPUT_PATH)

    with open(ENRICHED_SECTIONS_JSON, 'r', encoding='utf-8') as f:
        default_sections = json.load(f)

        # Dynamic iteration over enriched keys
    default_sections = json.load(open(ENRICHED_SECTIONS_JSON, encoding="utf-8"))
    updated_sections = {}


    

    def rewrite_section(section_name, original_text):
        prompt = f"""
    You are a LaTeX resume editor working for Mohamed Sahad.

    Your job is to **rewrite the LaTeX content only if needed** to match the job more closely, while preserving formatting, section structure, and tone.

    --- PERSONAL PROFILE ---
    The following is Mohamed Sahad's real background information. ONLY use these verified achievements, skills, projects, and experiences when rewriting. DO NOT hallucinate or invent anything that’s not explicitly supported here.

    {PERSONAL_PROFILE}

    --- JOB INPUT ---
    - Job Title: {job_title}
    - Company: {company_name}
    - Location: {location or 'Not specified'}
    - Job Description:
    {job_description}

    --- CURRENT SECTION ---
    Below is Mohamed's current "{section_name}" section from his resume:
    {original_text}

    --- INSTRUCTIONS ---

    1. Return only valid **LaTeX code** (e.g., \resumeSubItem{{}}{{...}} or \item ...). No prose, no explanation.
    2. Do **not escape** LaTeX commands like \item, \resumeSubItem, \resumeProject.
    3. Do escape special characters like %, $, &, #, _, ~ only **inside the text content**.
    4. NEVER include natural language like “Certainly”, “Here’s your section”, “Below is...”, etc.
    5. Maintain the original structure and spacing. Only update the bullet or sentence contents if needed.
    6. Ensure the entire final resume stays within **2 pages only** — keep length of each bullet **similar** to original.

    --- SECTION-SPECIFIC RULES ---

    - **EXECUTIVE SUMMARY**:
        - Keep it very close to original unless there's obvious value in changing.
        - Must be output using: \resumeSubItem{{}}{{...}}

    - **EXPERIENCE** and **PROJECTS**:
        - Must return exactly **2 bullet points** per project.
        - If truly essential, you may use up to **3 bullets**, but NEVER more.
        - Combine all important ideas from longer original bullets into fewer bullets **without losing meaning or keywords**.
        - Must use: \item Bullet content...
        - Start each bullet with a strong **action verb**.
        - Make results **quantifiable** where possible.
        - Bullet should use **job-relevant keywords** from the description.
        - Avoid **repeating words or phrases**.
        - Keep bullets concise, informative, and **ATS-friendly**.

    - **SKILLS**:
        - For categories like "Programming", "Soft Skills", etc., DO NOT remove existing skills.
        - Do **not duplicate** any skill across multiple categories.
        - Do **not add any skill** that is not clearly related to Mohamed's background in the personal profile (education, projects, experience).
        - You may add job-relevant skills only if there is evidence in the profile or resume.
        - Format new additions as:
        \resumeSubItem{{Category}}{{Skill1 (Level),  Skill2,  Skill3}}
        - Use **commas only**, not pipes (|), to separate skills.
        - If a job demands a skill that is **not in the profile**, you may add it with **(Basic)** only.
        - If a skill is **somewhat known** but not listed, add it with at least **(Intermediate)**.

    Return only the updated **LaTeX-formatted block**. No extra explanation.
    """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You ONLY return raw LaTeX code using \\item or \\resumeSubItem. Never add explanations or markdown formatting."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()


    for key in extract_section_keys(ENRICHED_SECTIONS_JSON):
        gpt_output = rewrite_section(key, default_sections[key])
        gpt_output = strip_markdown(gpt_output)
        updated_sections[key] = gpt_output


        # -------- FILL TEMPLATE --------
    rendered_tex =  template.render(**updated_sections)
    Path("output").mkdir(exist_ok=True)
    with open(OUTPUT_TEX, "w", encoding="utf-8") as f:
        f.write(rendered_tex)


    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-output-directory=output", "output/resume_generated.tex"],
        capture_output=True,
        text=True
    )

    # Show error log if LaTeX failed
    if result.returncode != 0:
        print("❌ LaTeX compile failed:\n")
        print(result.stdout)
        print("\n--- STDERR ---\n")
        print(result.stderr)
    else:
        print("✅ PDF compiled successfully.")

        return rendered_tex, OUTPUT_PDF

        

# ========== FUNCTION 3: GENERATE COVER LETTER ==========
def generate_cover_letter_body(job_title, company_name, location, job_description, output_dir):
    with open(PROFILE_TXT_PATH, "r", encoding="utf-8") as f:
        personal_profile = f.read().strip()

    prompt = f"""
You are a professional LaTeX-based cover letter writer for Mohamed Sahad.
Your job is to write the **main body of the cover letter only**, in formal, concise, and job-aligned prose, based on Mohamed's verified personal background and the job description.

--- PERSONAL PROFILE ---
{personal_profile}

--- JOB INPUT ---
- Job Title: {job_title}
- Company: {company_name}
- Location: {location or 'Not specified'}
- Job Description:
{job_description}

--- INSTRUCTIONS ---

1. Your output must be **valid LaTeX**.
2. Do **not escape** LaTeX commands like `\\n`, `\\textbf`, etc.
3. Do escape special LaTeX characters like `%`, `$`, `&`, `#`, `_`, `~` **inside sentences**.
4. Do **not** include salutation (e.g., “Dear Hiring Manager”) or signature.
5. Focus only on the **core body** between those two.
6. Write 2–4 short paragraphs max. Keep language clean, professional, and targeted.
7. Use keywords and relevant skills from the job description if they align with Mohamed’s actual experience.
8. Do not hallucinate — base all content strictly on Mohamed’s actual profile.
9. NEVER include markdown-style formatting like triple backticks (```latex ... ```) around the output.

Only return LaTeX-compatible body content. Nothing else.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You return only the raw LaTeX content for the body of the cover letter. Never include natural language explanations."},
            {"role": "user", "content": prompt}
        ]
    )

    body = strip_markdown_fences(response.choices[0].message.content)

    escaped_title = escape_latex(job_title)
    escaped_company = escape_latex(company_name)
    escaped_location = escape_latex(location)
    company_info = f"{escaped_company} \\\\ {escaped_location}"

    data = {
        "job_title": escaped_title,
        "company_info": company_info,
        "cover_letter_body": body
    }

    with open(JSON_SECTIONS_COVER_LETTER, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    template = LATEX_ENV.get_template(TEX_TEMPLATE_COVER)
    rendered_tex = template.render(data)

    tex_path = os.path.join(output_dir, "cover_letter.tex")
    pdf_path = os.path.join(output_dir, "cover_letter.pdf")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(rendered_tex)

    run_latex(tex_path, output_dir)
    return rendered_tex, pdf_path
