#!/usr/bin/env python3
"""Generate the 7 lab report PDFs for ENSP461 Lab 1 - Meenakshi Rakesh.

Run inside WSL Ubuntu with the repo venv:
    /home/meenakshi/ensp461-lab1/.venv/bin/python "<this file>"
"""
import html as htmlmod
import os
import re
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Image, Table, TableStyle, PageBreak,
                                Preformatted, KeepTogether)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

# ---------------------------------------------------------------- paths
WIN = "/mnt/c/Users/Abhinav/DevOps & Automation Lab/Lab1-Meenakshi"
SHOTS = os.path.join(WIN, "screenshots")
LOGS = os.path.join(WIN, "logs")
OUT = os.path.join(WIN, "reports")
REPO = "/home/meenakshi/ensp461-lab1"
os.makedirs(OUT, exist_ok=True)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
for f in (MONO, MONO_B, SANS, SANS_B):
    if not os.path.exists(f):
        sys.exit("missing font: " + f)
pdfmetrics.registerFont(TTFont("Mono", MONO))
pdfmetrics.registerFont(TTFont("MonoB", MONO_B))
pdfmetrics.registerFont(TTFont("Sans", SANS))
pdfmetrics.registerFont(TTFont("SansB", SANS_B))

TITLE = "ENSP461 - DevOps & Automation | Lab 1: DevOps Foundations & Continuous Integration"
NAME = "Meenakshi Rakesh"
ROLL = "2301730144"
HDR = "Name: %s        Roll No.: %s        Environment: Ubuntu 24.04 LTS (WSL2)" % (NAME, ROLL)
GITHUB = "https://github.com/meenakshi16rp/Devops-lab-1-"

st_body = ParagraphStyle("body", fontName="Sans", fontSize=10, leading=14)
st_bullet = ParagraphStyle("bullet", parent=st_body, leftIndent=14, bulletIndent=6)
st_h2 = ParagraphStyle("h2", fontName="SansB", fontSize=13, leading=17, spaceBefore=10, spaceAfter=5)
st_h3 = ParagraphStyle("h3", fontName="SansB", fontSize=11, leading=15, spaceBefore=6, spaceAfter=3)
st_code = ParagraphStyle("code", fontName="Mono", fontSize=7.6, leading=10,
                         textColor=colors.HexColor("#111111"))
st_code_small = ParagraphStyle("codes", fontName="Mono", fontSize=6.4, leading=8.6,
                               textColor=colors.HexColor("#111111"))
st_code_label = ParagraphStyle("codel", fontName="MonoB", fontSize=8, leading=11,
                               textColor=colors.black, spaceBefore=6, spaceAfter=2)
st_cap = ParagraphStyle("cap", fontName="Sans", fontSize=8.5, leading=11, alignment=TA_LEFT,
                        textColor=colors.black, spaceBefore=2, spaceAfter=8)
st_tbl = ParagraphStyle("tbl", fontName="Sans", fontSize=8.5, leading=11)


def read(path, root=LOGS, limit=None):
    fp = os.path.join(root, path)
    with open(fp, "r", errors="replace") as fh:
        t = fh.read()
    if limit:
        t = t[:limit]
    return t


def repo_file(path):
    with open(os.path.join(REPO, path), "r", errors="replace") as fh:
        return fh.read()


def polling_log_text():
    """Extract the plain polling log from the saved Jenkins page."""
    html = read("git-polling-log.txt")
    m = re.search(r"<h1>Git Polling Log</h1><pre>(.*?)</pre>", html, re.S)
    if not m:
        return "polling log unavailable"
    txt = re.sub(r"<[^>]+>", "", m.group(1))
    return htmlmod.unescape(txt).strip()


class Doc(BaseDocTemplate):
    def __init__(self, path, qtitle, marks):
        self.qtitle = qtitle
        self.marks = marks
        BaseDocTemplate.__init__(self, path, pagesize=A4,
                                 leftMargin=2 * cm, rightMargin=2 * cm,
                                 topMargin=2.2 * cm, bottomMargin=1.8 * cm,
                                 title=qtitle, author=NAME)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=self.deco)])

    def deco(self, canv, doc):
        canv.saveState()
        canv.setFont("SansB", 10.5)
        canv.setFillColor(colors.black)
        canv.drawString(2 * cm, A4[1] - 1.4 * cm, TITLE)
        canv.setFont("Sans", 9.5)
        canv.drawString(2 * cm, A4[1] - 1.85 * cm, HDR)
        canv.setStrokeColor(colors.black)
        canv.setLineWidth(0.7)
        canv.line(2 * cm, A4[1] - 2.05 * cm, A4[0] - 2 * cm, A4[1] - 2.05 * cm)
        canv.setFont("Sans", 8)
        canv.drawCentredString(A4[0] / 2, 1.1 * cm, "Page %d" % doc.page)
        canv.restoreState()


def h(story, text, style=st_h2):
    story.append(Paragraph(text, style))


def p(story, text):
    story.append(Paragraph(text, st_body))


def bullets(story, items):
    for it in items:
        story.append(Paragraph(it, st_bullet, bulletText="-"))
    story.append(Spacer(1, 4))


def code(story, text, label=None, small=False):
    if label:
        story.append(Paragraph(label, st_code_label))
    # fold over-long lines so nothing clips at the right margin
    limit = 108 if small else 92
    out = []
    for ln in text.split("\n"):
        while len(ln) > limit:
            cut = ln.rfind(" ", 40, limit)
            if cut < 40:
                cut = limit
            out.append(ln[:cut] + " \\")
            ln = "      " + ln[cut:].lstrip()
        out.append(ln)
    text = "\n".join(out)
    # Preformatted draws text literally - no XML escaping needed
    story.append(Preformatted(text, st_code_small if small else st_code))
    story.append(Spacer(1, 6))


def shot(story, fname, caption, max_w=16.2 * cm, max_h=17.5 * cm):
    fp = os.path.join(SHOTS, fname)
    if not os.path.exists(fp):
        story.append(Paragraph("[missing screenshot: %s]" % fname, st_cap))
        return
    iw, ih = PILImage.open(fp).size
    scale = min(max_w / iw, max_h / ih, 1.0)
    img = Image(fp, width=iw * scale, height=ih * scale)
    img.hAlign = "CENTER"
    story.append(KeepTogether([img, Paragraph("Figure: " + caption, st_cap)]))


def cover_block(story, qtitle, marks, intro):
    story.append(Paragraph(qtitle, ParagraphStyle(
        "qt", fontName="SansB", fontSize=14, leading=18, spaceAfter=8)))
    p(story, "Executed on Ubuntu 24.04 LTS (WSL2) by Meenakshi Rakesh. Repository: "
             "<b>%s</b>" % GITHUB)
    story.append(Spacer(1, 8))


def tbl(story, header, rows, widths):
    data = [[Paragraph("<b>%s</b>" % c, st_tbl) for c in header]] + \
           [[Paragraph(str(c), st_tbl) for c in r] for r in rows]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9D9D9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FB")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story.append(t)
    story.append(Spacer(1, 8))


def arch_diagram(story):
    """Draw the CI/CD architecture flow."""
    d = Drawing(16.2 * cm, 7.2 * cm)
    bw, bh, gap = 2.68 * cm, 1.7 * cm, 0.7 * cm
    y0 = 4.5 * cm
    boxes = [
        ("Developer", "git push (Meenakshi)", "#DCEBFF"),
        ("GitHub", "Devops-lab-1- (main)", "#D6F5D6"),
        ("Jenkins", "poll SCM H/5 * * * *", "#FFF3CC"),
        ("Pipeline", "Build-Test-Deploy", "#FFE0CC"),
        ("Deployment", "Flask app :5000", "#E8DDFF"),
    ]
    x = 0.15 * cm
    for i, (l1, l2, col) in enumerate(boxes):
        d.add(Rect(x, y0, bw, bh, fillColor=colors.HexColor(col),
                   strokeColor=colors.HexColor("#335577"), strokeWidth=0.8))
        d.add(String(x + bw / 2, y0 + bh - 14, l1, fontName="SansB", fontSize=6.5,
                     textAnchor="middle", fillColor=colors.black))
        d.add(String(x + bw / 2, y0 + bh - 26, l2, fontName="Sans", fontSize=5.6,
                     textAnchor="middle", fillColor=colors.black))
        if i < len(boxes) - 1:
            ax = x + bw
            d.add(Line(ax + 2, y0 + bh / 2, ax + gap - 8, y0 + bh / 2,
                       strokeColor=colors.HexColor("#335577"), strokeWidth=1))
            d.add(Polygon([ax + gap - 8, y0 + bh / 2 + 3, ax + gap - 8, y0 + bh / 2 - 3,
                           ax + gap - 2, y0 + bh / 2], fillColor=colors.HexColor("#335577"),
                          strokeColor=None))
        x += bw + gap
    d.add(String(0.15 * cm, y0 - 0.65 * cm,
                 "Feedback loop: after a successful build the deployed app is verified with curl http://localhost:5000/health -> HTTP 200 {\"status\": \"UP\"}",
                 fontName="Sans", fontSize=6.5, fillColor=colors.black))
    d.add(String(0.15 * cm, y0 + bh + 0.45 * cm,
                 "Automation trigger: GitHub commit -> Jenkins SCM poll (every 5 min) -> pipeline run (no manual step)",
                 fontName="Sans", fontSize=6.5, fillColor=colors.black))
    story.append(d)
    story.append(Spacer(1, 6))


# ================================================================ reports

def r1_records():
    s = []
    d = Doc(os.path.join(OUT, "1-record-all-commands.pdf"),
            "Question 1 - Records of all experiments", 5)
    cover_block(s, "Question 1: Record all commands, pipeline configurations, screenshots, "
                "commit history, and observations for each experiment.", 5,
                "This document compiles the evidence of every experiment in Lab 1 as executed by "
                "Meenakshi Rakesh: the commands run on Ubuntu 24.04 LTS (WSL2), the pipeline "
                "configuration, the Git commit history, screenshots of each step, and the "
                "observations drawn from them. All artefacts are also maintained in the GitHub "
                "repository <b>%s</b>." % GITHUB)

    h(s, "1. Environment and service verification")
    shot(s, "04-terminal-env-verify.png", "Ubuntu terminal: environment and Jenkins service verification "
         "(user meenakshi, Ubuntu 24.04.3, Git 2.43.0, Jenkins 2.580.2 active)")

    h(s, "2. Commit history (github.com/meenakshi16rp/Devops-lab-1-)")
    code(s, read("git-history-and-config.txt"), "git log --graph, config and remotes")
    shot(s, "05-github-commit-history.png", "Commit history on GitHub - meaningful messages, merge commit visible")

    h(s, "2. Git installation and configuration (Q4)")
    code(s, "sudo apt update && sudo apt install -y git\ngit config --global user.name \"Meenakshi\"\n"
            "git config --global user.email \"meenakshi16rp@gmail.com\"\n"
            "git config --global init.defaultBranch main\n"
            "git config --global credential.helper store\ngit config --global --list",
         "installation and global configuration")
    shot(s, "04-terminal-git-config.png", "Terminal verification: user meenakshi, Ubuntu 24.04.3, "
         "git 2.43.0 and the global configuration")

    h(s, "3. Jenkins installation and first-time setup (Q4)")
    code(s, "sudo apt install -y openjdk-21-jdk\n"
            "curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key -o /usr/share/keyrings/jenkins-keyring.asc\n"
            "echo \"deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/\" "
            "| sudo tee /etc/apt/sources.list.d/jenkins.list\n"
            "sudo apt update && sudo apt install -y jenkins\n"
            "sudo systemctl enable --now jenkins\n"
            "sudo systemctl is-active jenkins\nactive\njenkins --version\n2.580.2",
         "Jenkins LTS installation (systemd service on port 8080)", small=True)
    shot(s, "04-jenkins-unlock-page.png", "Unlock Jenkins with the initial admin password")
    shot(s, "04-jenkins-customize-plugins.png", "Customize Jenkins - install suggested plugins")
    shot(s, "04-jenkins-dashboard-ready.png", "Jenkins dashboard ready (admin user: meenakshi)")

    h(s, "4. Version control workflow (Q5)")
    code(s, "cd ~/ensp461-lab1\ngit init -b main\ngit add README.md .gitignore app/app.py "
            "app/requirements.txt app/tests/test_app.py\ngit commit -m \"Initial commit: sample Flask "
            "application with unit tests\"\ngit add deploy/deploy.sh\ngit commit -m \"Add automated "
            "deployment script with health verification\"\ngit checkout -b feature/app-info-endpoint\n"
            "# ... implemented /info endpoint + unit test on the branch ...\n"
            "git add app/ && git commit -m \"Add /info endpoint with application metadata and unit test\"\n"
            "git checkout main\ngit merge --no-ff feature/app-info-endpoint -m \"Merge "
            "feature/app-info-endpoint: add /info endpoint to main\"\ngit add Jenkinsfile\ngit commit -m "
            "\"Add declarative Jenkinsfile with build, test and deploy stages\"\ngit remote add origin "
            + GITHUB + ".git\ngit push -u origin main\ngit push -u origin feature/app-info-endpoint",
            "init, stage, commit, branch, merge, push")
    shot(s, "05-terminal-git-state.png", "Ubuntu terminal: resulting commit graph, branches and remotes")
    shot(s, "05-github-repo-home.png", "Repository on GitHub: 8 commits, 2 branches, Jenkinsfile and README")

    h(s, "5. Pipeline job and Jenkinsfile execution (Q6/Q7)")
    code(s, "Jenkins job:        ensp461-lab1-pipeline (Pipeline)\n"
            "Definition:         Pipeline script from SCM\nSCM:                Git\n"
            "Repository URL:     " + GITHUB + ".git\n"
            "Credentials:        github-creds (meenakshi16rp /****** GitHub PAT)\n"
            "Branch:             */main\nScript path:        Jenkinsfile\n"
            "Build trigger:      Poll SCM -> H/5 * * * *\n"
            "Post-build:         post { success / failure / always { cleanWs() } }",
            "job configuration summary")
    code(s, read("build1-console.txt")[-1300:], "build #1 console output (tail) - FAILURE, defect diagnosed", small=True)
    code(s, read("build2-console.txt")[-900:], "build #2 console output (tail) - SUCCESS after the fix", small=True)
    shot(s, "06-pipeline-job-page.png", "Pipeline job page (GitHub project link, stages, polling log)")
    shot(s, "07-build2-stage-graph.png", "Build #2 stage graph: all stages green")

    h(s, "6. Automated deployment (Q3)")
    code(s, "Build trigger: Poll SCM - H/5 * * * *  (every 5 minutes)\n"
            "deploy step:   ./deploy/deploy.sh  (reuses the Build stage virtualenv,\n"
            "               restarts the app, verifies http://localhost:5000/health)",
            "trigger and deployment steps")
    code(s, polling_log_text(), "git-polling-log.txt - poll detects commit eaa01d3 -> build #3", small=True)
    code(s, "meenakshi@ubuntu:~$ curl -s http://localhost:5000/health\n{\"status\":\"UP\"}\n"
            "meenakshi@ubuntu:~$ curl -s http://localhost:5000/info\n"
            "{\"app\":\"ensp461-lab1-sample-app\",\"author\":\"Meenakshi\","
            "\"pipeline\":\"Jenkins declarative CI/CD\",\"version\":\"1.0.0\"}",
            "deployed application verified after build #3")
    shot(s, "03-build3-scm-triggered.png", "Build #3 - cause: 'Started by an SCM change' (automatic trigger)")
    shot(s, "03-deployed-app-terminal.png", "Deployed Flask application verified on port 5000")

    h(s, "7. Pipeline configuration file (Jenkinsfile)")
    code(s, repo_file("Jenkinsfile"), "committed at the repository root")

    h(s, "9. Observations (summary)")
    bullets(s, [
        "Build #1 failed in the Deploy stage (curl exit code 7): the deployment script invoked the "
        "system python3, which does not have Flask installed - diagnosed from the console log "
        "(<b>ModuleNotFoundError: No module named 'flask'</b>).",
        "Fix: deploy.sh now reuses the virtual environment created in the Build stage (<b>VENV</b>) "
        "and retries the health check; committed as c9df47c, after which build #2 succeeded.",
        "Jenkins' process-tree killer stopped the deployed app after the build ended; setting "
        "<b>JENKINS_NODE_COOKIE=dontKillMe</b> keeps it running (commit eaa01d3).",
        "Build #3 fired with cause <b>Started by an SCM change</b> - the Poll SCM trigger automates "
        "the whole chain from git push to deployment without manual steps.",
        "Meaningful commit messages keep the history self-documenting; the pipeline is reproducible "
        "from the repository alone (Jenkinsfile + deploy script)."])
    d.build(s)


def r2_workflow():
    s = []
    d = Doc(os.path.join(OUT, "2-cicd-workflow-report.pdf"),
            "Question 2 - CI/CD workflow report", 10)
    cover_block(s, "Question 2: Prepare a CI/CD workflow report describing the pipeline "
                "architecture, stages, automation results, and observations with supporting "
                "screenshots.", 10,
                "This report describes the continuous integration / continuous delivery workflow "
                "built for the sample Flask application. Everything shown was executed on Ubuntu "
                "24.04 LTS (WSL2) by Meenakshi Rakesh; the pipeline is defined as code in the "
                "repository's Jenkinsfile.")

    h(s, "1. Pipeline architecture")
    arch_diagram(s)
    bullets(s, [
        "<b>Source control:</b> GitHub repository Devops-lab-1- (main branch) owned by meenakshi16rp; "
        "the developer pushes commits with a feature-branch workflow.",
        "<b>Automation trigger:</b> Jenkins polls the repository every 5 minutes (H/5 * * * *). "
        "When new commits are found the pipeline starts on its own - no manual build step.",
        "<b>CI/CD engine:</b> Jenkins 2.580.2 LTS with a declarative pipeline (Jenkinsfile) checked "
        "out from the same repository - the pipeline itself is version controlled.",
        "<b>Target:</b> the built application is deployed to a local deployment directory and served "
        "on port 5000; the pipeline verifies the health endpoint before declaring success."])

    h(s, "2. Pipeline stages")
    tbl(s, ["Stage", "What it does", "Tool / command", "Result"],
        [["Checkout SCM", "Jenkins fetches the Jenkinsfile from main", "Git + github-creds", "1 s, OK"],
         ["Checkout", "Pulls source code of the latest commit", "checkout scm", "1 s, OK"],
         ["Build", "Creates a Python virtual environment and installs dependencies",
          "python3 -m venv + pip install -r app/requirements.txt", "8 s, OK"],
         ["Test", "Runs the unit test suite", "pytest app/tests -v (3 tests)", "0.75 s, OK"],
         ["Deploy", "Copies the app to the deploy directory, (re)starts it, verifies health",
          "./deploy/deploy.sh + curl :5000/health", "2 s, OK"],
         ["Post Actions", "Success/failure notification echo; workspace cleanup", "post + cleanWs()", "0.38 s, OK"]],
        [3.2 * cm, 6.2 * cm, 4.3 * cm, 2.5 * cm])

    h(s, "3. Automation results")
    tbl(s, ["Build", "Trigger", "Commit", "Result", "Duration"],
        [["#1", "Manual (first run)", "eedda81", "FAILURE (Deploy stage)", "30.6 s"],
         ["#2", "Manual (after fix)", "c9df47c", "SUCCESS", "18.7 s"],
         ["#3", "Automatic - Started by an SCM change", "eaa01d3", "SUCCESS", "18.3 s"]],
        [1.7 * cm, 5.6 * cm, 2.2 * cm, 4.2 * cm, 2.5 * cm])
    bullets(s, [
        "All three unit tests (index, health, info) pass in every successful build.",
        "The deployed application answers /health with {\"status\":\"UP\"} and /info reports "
        "author Meenakshi and the Jenkins declarative CI/CD pipeline."])

    h(s, "4. Evidence")
    shot(s, "07-build2-stage-graph.png", "Stage graph of a complete successful run")
    shot(s, "03-git-polling-log.png", "Git polling log: the poll detects the new commit and reports 'Changes found'")
    shot(s, "03-build3-scm-triggered.png", "Build #3 was started automatically by an SCM change")
    shot(s, "03-deployed-app-terminal.png", "Deployed application verified live on port 5000")

    h(s, "5. Observations")
    bullets(s, [
        "Pipelines-as-code made the whole workflow reproducible: recreating the job only requires "
        "pointing Jenkins at the repository.",
        "The first run failed exactly where an undebugged script typically fails (deployment "
        "environment); the console log pinpointed the missing Flask module within seconds - a good "
        "demonstration of why each stage should fail fast.",
        "Poll SCM is a simple, reliable trigger for environments where GitHub cannot reach the "
        "Jenkins host for webhooks (the WSL2 lab is not publicly reachable).",
        "Cleanup (cleanWs) in the post section keeps the workspace small across builds."])
    d.build(s)


def r3_deploy():
    s = []
    d = Doc(os.path.join(OUT, "3-automate-deployment.pdf"),
            "Question 3 - Automate application deployment", 5)
    cover_block(s, "Question 3: Automate application deployment using Jenkins by configuring "
                "build triggers, post-build actions, and deployment steps.", 5,
                "Deployment is fully automated: Jenkins polls GitHub for new commits, builds and "
                "tests the application, deploys it to the local deployment directory, and verifies "
                "the running service - all inside the same pipeline run.")

    h(s, "1. Build trigger configuration")
    code(s, "Build Triggers -> Poll SCM\nSchedule: H/5 * * * *   (every 5 minutes, hash-distributed minute)",
         "job configuration")
    p(s, "Because the WSL2 lab environment is not reachable from the public internet, GitHub cannot "
         "deliver webhooks; SCM polling achieves the same automation by having Jenkins check GitHub "
         "for new commits on a schedule.")

    h(s, "2. Deployment steps (deploy stage + deploy.sh)")
    code(s, repo_file("deploy/deploy.sh"), "deploy/deploy.sh (committed to the repository)")

    h(s, "3. Post-build actions")
    code(s, "post {\n    success { echo \"Pipeline SUCCESS: application built, tested and deployed.\" }\n"
            "    failure { echo \"Pipeline FAILED - check the stage logs.\" }\n"
            "    always { echo \"Cleaning workspace temporary files...\"; cleanWs() }\n}",
         "Jenkinsfile post section")
    code(s, "[Pipeline] echo\nPipeline SUCCESS: application built, tested and deployed.\n"
            "[WS-CLEANUP] Deleting project workspace...\n[WS-CLEANUP] done\nFinished: SUCCESS",
         "build #2 console output (post actions)")

    h(s, "4. Proof of the automated trigger")
    code(s, polling_log_text(), "git-polling-log.txt - the poll detects commit eaa01d3 (Changes found)", small=True)
    shot(s, "03-git-polling-log.png", "Git polling log in Jenkins")
    shot(s, "03-build3-scm-triggered.png", "Build #3 - cause: 'Started by an SCM change', result SUCCESS")

    h(s, "5. Deployed application verification")
    shot(s, "03-deployed-app-terminal.png", "The app deployed by build #3 answers on http://localhost:5000")
    code(s, "curl -s http://localhost:5000/health\n{\"status\":\"UP\"}\n"
            "curl -s http://localhost:5000/info\n{\"app\":\"ensp461-lab1-sample-app\","
            "\"author\":\"Meenakshi\",\"pipeline\":\"Jenkins declarative CI/CD\",\"version\":\"1.0.0\"}",
         "health and info endpoints after the automated build")

    h(s, "6. Observations")
    bullets(s, [
        "The first automated attempt (build #1) failed because the deploy script used the system "
        "Python without Flask; reusing the pipeline virtualenv fixed it - the fix itself went through "
        "the same automated pipeline.",
        "Jenkins kills child processes at the end of a build; JENKINS_NODE_COOKIE=dontKillMe keeps "
        "the deployed service alive after the run.",
        "The retry loop around the health check makes the Deploy stage robust against slow startups."])
    d.build(s)


def r4_git_jenkins():
    s = []
    d = Doc(os.path.join(OUT, "4-install-configure-git-jenkins.pdf"),
            "Question 4 - Install and configure Git and Jenkins", 5)
    cover_block(s, "Question 4: Install and configure Git on Ubuntu Linux, verify the "
                "installation, and set up global Git configuration (user name and email).", 5,
                "Git 2.43.0 and Jenkins 2.580.2 LTS were installed on Ubuntu 24.04.3 LTS (WSL2) "
                "under the user <b>meenakshi</b>. All commands were executed in the Ubuntu terminal.")

    h(s, "1. System and Git installation")
    code(s, "meenakshi@ubuntu:~$ lsb_release -d\nDescription:    Ubuntu 24.04.3 LTS\n"
            "meenakshi@ubuntu:~$ sudo apt update && sudo apt install -y git\n"
            "meenakshi@ubuntu:~$ git --version\ngit version 2.43.0", "installation and verification")

    h(s, "2. Global Git configuration")
    code(s, "git config --global user.name \"Meenakshi\"\n"
            "git config --global user.email \"meenakshi16rp@gmail.com\"\n"
            "git config --global init.defaultBranch main\n"
            "git config --global credential.helper store\ngit config --global core.editor nano",
         "configuration commands")
    code(s, "meenakshi@ubuntu:~$ git config --global --list\n"
            "user.name=Meenakshi\nuser.email=meenakshi16rp@gmail.com\n"
            "init.defaultbranch=main\ncore.editor=nano\ncredential.helper=store",
         "verification")
    shot(s, "04-terminal-git-config.png", "Ubuntu terminal: meenakshi@ubuntu prompt, Ubuntu 24.04.3, "
         "Git 2.43.0 and the global configuration")

    h(s, "3. Jenkins installation")
    code(s, "sudo apt install -y openjdk-21-jdk\ncurl -fsSL https://pkg.jenkins.io/debian-stable/"
            "jenkins.io-2023.key -o /usr/share/keyrings/jenkins-keyring.asc\n"
            "echo \"deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] "
            "https://pkg.jenkins.io/debian-stable binary/\" | sudo tee /etc/apt/sources.list.d/jenkins.list\n"
            "sudo apt update && sudo apt install -y jenkins\nsudo systemctl enable --now jenkins\n"
            "sudo systemctl is-active jenkins\nactive\njenkins --version\n2.580.2",
         "Jenkins LTS installation (systemd service on port 8080)", small=True)

    h(s, "4. Jenkins first-run configuration")
    p(s, "The setup wizard was completed in the browser at http://localhost:8080: unlock with the "
         "initial admin password, install the suggested plugins (Pipeline, Git, GitHub Branch "
         "Source, Credentials Binding, ...), and create the administrator account.")
    shot(s, "04-jenkins-unlock-page.png", "Unlock Jenkins - initial admin password from "
         "/var/lib/jenkins/secrets/initialAdminPassword")
    shot(s, "04-jenkins-customize-plugins.png", "Customize Jenkins - install suggested plugins")
    shot(s, "04-jenkins-dashboard-ready.png", "Jenkins dashboard ready (admin user: meenakshi)")

    h(s, "5. Observations")
    bullets(s, [
        "Jenkins runs as a systemd service (user jenkins, JAVA 21) and survived WSL restarts.",
        "The initial admin password file is removed after unlocking; plugins install directly from "
        "the official update center.",
        "Global Git identity ensures every commit made in the lab is attributed to Meenakshi."])
    d.build(s)


def r5_version_control():
    s = []
    d = Doc(os.path.join(OUT, "5-version-control-git.pdf"),
            "Question 5 - Set up version control using Git", 5)
    cover_block(s, "Question 5: Initialize a repository, stage and commit changes, create "
                "branches, merge branches, and push the repository to GitHub.", 5,
                "The complete version-control workflow was performed on the sample Flask "
                "application repository and pushed to GitHub (%s)." % GITHUB)

    h(s, "1. Initialize, stage and commit")
    code(s, "cd ~/ensp461-lab1\ngit init -b main\ngit add README.md .gitignore app/app.py "
            "app/requirements.txt app/tests/test_app.py\ngit commit -m \"Initial commit: sample Flask "
            "application with unit tests\"\ngit add deploy/deploy.sh\ngit commit -m \"Add automated "
            "deployment script with health verification\"", "init, stage, commit")

    h(s, "2. Branch, feature work and merge")
    code(s, "git checkout -b feature/app-info-endpoint\n"
            "# implement /info endpoint + unit test on the branch\n"
            "git add app/ && git commit -m \"Add /info endpoint with application metadata and unit test\"\n"
            "git checkout main\ngit merge --no-ff feature/app-info-endpoint -m \"Merge "
            "feature/app-info-endpoint: add /info endpoint to main\"", "branch and merge (--no-ff)")
    code(s, read("git-history-and-config.txt"), "commit history after the merge (git log --graph)")

    h(s, "3. Push to GitHub")
    code(s, "git remote add origin " + GITHUB + ".git\ngit push -u origin main\n"
            "git push -u origin feature/app-info-endpoint", "remote and push")
    shot(s, "05-github-repo-home.png", "Repository on GitHub: 7 commits, 2 branches, Jenkinsfile and README visible")
    shot(s, "05-github-commit-history.png", "Commit history on GitHub - merge commit and feature branch visible")
    shot(s, "05-github-branches.png", "Branches page: main (default) and feature/app-info-endpoint")

    h(s, "4. Observations")
    bullets(s, [
        "--no-ff merging keeps the feature branch visible in history, which documents the workflow.",
        "Every commit message describes <i>what</i> changed so the log reads as a narrative.",
        "The feature branch remains on GitHub as evidence of the branching workflow.",
        "credential.helper store keeps the PAT outside the repository (in ~/.git-credentials, chmod 600)."])
    d.build(s)


def r6_pipeline():
    s = []
    d = Doc(os.path.join(OUT, "6-basic-jenkins-pipeline.pdf"),
            "Question 6 - Basic Jenkins CI/CD pipeline", 5)
    cover_block(s, "Question 6: Implement a basic Jenkins CI/CD pipeline that pulls source code "
                "from the GitHub repository and triggers an automated build.", 5,
                "A Jenkins pipeline job was created that pulls the source code from the GitHub "
                "repository and builds it automatically. Jenkins stores the GitHub PAT as a "
                "credential (github-creds) so the private checkout works without exposing the token.")

    h(s, "1. Credential setup")
    code(s, "Manage Jenkins -> Credentials -> System -> Global -> Add Credentials\n"
            "Kind:          Username with password\nUsername:      meenakshi16rp\n"
            "Password:      ghp_**************** (GitHub PAT, repo scope)\n"
            "ID:            github-creds", "stored credential")

    h(s, "2. Job configuration")
    code(s, "New Item -> ensp461-lab1-pipeline -> Pipeline\n"
            "Definition:     Pipeline script from SCM\nSCM:            Git\n"
            "Repository URL: " + GITHUB + ".git\n"
            "Credentials:    github-creds\nBranch:         */main\nScript path:    Jenkinsfile\n"
            "Build trigger:  Poll SCM - H/5 * * * *", "job configuration")
    shot(s, "06-pipeline-job-page.png", "Pipeline job page after configuration (GitHub project link, stages, polling log)")

    h(s, "3. First automated build (and a real defect)")
    p(s, "Build #1 pulled the source from GitHub and passed Checkout, Build and Test, but failed in "
         "the Deploy stage with exit code 7 (curl connection refused). The console log and the "
         "deploy.log identified the cause: the deploy script started the app with the system Python, "
         "which has no Flask module.")
    code(s, read("build1-console.txt")[-1400:], "build #1 console output (tail) - FAILURE", small=True)
    bullets(s, [
        "<b>Root cause:</b> ModuleNotFoundError: No module named 'flask' in the deployment runtime.",
        "<b>Fix:</b> deploy.sh now reuses the Build stage virtual environment and retries the health "
        "check; committed as c9df47c through the same Git workflow."])

    h(s, "4. Successful build")
    code(s, read("build2-console.txt")[0:1500], "build #2 console output (excerpt) - SUCCESS", small=True)
    shot(s, "07-build2-stage-view.png", "Build #2 result page: SUCCESS, started by user meenakshi, commit c9df47c")
    shot(s, "07-build2-stage-graph.png", "All pipeline stages green for build #2")

    h(s, "5. Observations")
    bullets(s, [
        "Pipeline-as-code means the job configuration in Jenkins stays minimal - the logic lives in "
        "the repository.",
        "The first failure demonstrated how console output plus stage granularity localize defects "
        "quickly.",
        "Jenkins attributing the build to 'meenakshi' and the commit to 'meenakshi16rp' confirms the "
        "identity configuration end to end."])
    d.build(s)


def r7_jenkinsfile():
    s = []
    d = Doc(os.path.join(OUT, "7-jenkinsfile-pipeline-stages.pdf"),
            "Question 7 - Jenkinsfile defining pipeline stages", 5)
    cover_block(s, "Question 7: Create a Jenkinsfile defining pipeline stages (build, test, deploy) "
                "and demonstrate a declarative or scripted pipeline execution.", 5,
                "A <b>declarative</b> Jenkinsfile defines the pipeline in four stages (Checkout, "
                "Build, Test, Deploy) plus post-build actions; it is executed by the "
                "ensp461-lab1-pipeline job directly from the repository.")

    h(s, "1. The Jenkinsfile (committed at the repository root)")
    code(s, repo_file("Jenkinsfile"), "Jenkinsfile")

    h(s, "2. Declarative pipeline structure")
    bullets(s, [
        "<b>pipeline { agent any }</b> - declarative syntax; runs on any available executor.",
        "<b>environment</b> block defines VENV (build virtualenv) and DEPLOY_DIR once for all stages.",
        "<b>stages:</b> Checkout (checkout scm) -> Build (venv + pip install) -> Test (pytest -v) "
        "-> Deploy (deploy.sh with health verification).",
        "<b>post</b> section reports success/failure and always cleans the workspace.",
        "echo steps make each stage's intent visible in the console log - useful for viva "
        "demonstration."])

    h(s, "3. Execution evidence")
    shot(s, "07-build2-stage-graph.png", "Stage graph: Checkout SCM, Checkout, Build, Test, Deploy, Post Actions - all successful")
    tbl(s, ["Stage", "Duration (build #2)", "Key step"],
        [["Checkout SCM", "1 s", "git fetch from GitHub"],
         ["Checkout", "1 s", "checkout scm"],
         ["Build", "8 s", "python3 -m venv + pip install"],
         ["Test", "0.75 s", "pytest: 3 passed"],
         ["Deploy", "2 s", "deploy.sh + health check OK"],
         ["Post Actions", "0.38 s", "success echo + cleanWs()"]],
        [4 * cm, 4 * cm, 8.2 * cm])
    code(s, "============================== 3 passed in 0.19s ===============================\n"
            "[Pipeline] echo\nDeploying application to local deployment directory...\n"
            "Deployment verified: health OK\nPipeline SUCCESS: application built, tested and deployed.\n"
            "Finished: SUCCESS", "console excerpt: test summary, deploy verification, final status")

    h(s, "4. Observations")
    bullets(s, [
        "Declarative pipelines give a fixed, readable structure (stages/steps/post) that maps "
        "directly onto the stage graph UI.",
        "Keeping the Jenkinsfile in the repository means every pipeline change is itself reviewed, "
        "versioned and built - CI for the CI definition.",
        "Stage timings show the build is dominated by dependency installation; caching could "
        "shorten it further."])
    d.build(s)


for fn in (r1_records, r2_workflow, r3_deploy, r4_git_jenkins,
           r5_version_control, r6_pipeline, r7_jenkinsfile):
    fn()
    print("generated:", fn.__name__)

print("done ->", OUT)
