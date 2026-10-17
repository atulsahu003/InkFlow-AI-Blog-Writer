const API_URL = "http://127.0.0.1:8000/api";

const $ = (id) => document.getElementById(id);

const form = $("blog-form");
const topicInput = $("topic");
const blogLengthInput = $("blog-length");
const writingToneInput = $("writing-tone");
const targetAudienceInput = $("target-audience");

const generateBtn = $("generate-btn");
const buttonText = $("button-text");
const buttonIcon = $("button-icon");

const progressCard = $("progress-card");
const progressTitle = $("progress-title");
const progressMessage = $("progress-message");
const progressPercentage = $("progress-percentage");
const progressFill = $("progress-fill");
const progressTrack = $("progress-track");

const workflowSteps = {
    research: $("step-research"),
    planning: $("step-planning"),
    writing: $("step-writing"),
    assembly: $("step-assembly"),
    proofreading: $("step-proofreading")
};

const resultSection = $("result-section");
const blogOutput = $("blog-output");
const sourcesCard = $("sources-card");
const sourcesList = $("sources-list");
const downloadBtn = $("download-btn");
const exportPdfBtn = $("export-pdf-btn");
const exportDocxBtn = $("export-docx-btn");
const copyBtn = $("copy-btn");
const errorMessage = $("error-message");

const editToggleBtn = $("edit-toggle-btn");
const editPanel = $("edit-panel");
const blogEditor = $("blog-editor");
const applyEditBtn = $("apply-edit-btn");
const cancelEditBtn = $("cancel-edit-btn");
const revisionInstructions = $("revision-instructions");
const regenerateBtn = $("regenerate-btn");
const regenerateButtonText = $("regenerate-button-text");
const revisionStatus = $("revision-status");

let currentBlog = "";
let currentSources = [];
let completedWritingSections = 0;
let totalWritingSections = 5;

const workflowOrder = [
    "research",
    "planning",
    "writing",
    "assembly",
    "proofreading"
];

const stageProgress = {
    starting: 5,
    working: 8,
    research: 20,
    planning: 40,
    writing: 45,
    assembly: 82,
    proofreading: 92,
    complete: 100
};


// -------------------- General helpers --------------------

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}

function clearError() {
    errorMessage.textContent = "";
    errorMessage.classList.add("hidden");
}

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, (character) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

function getExportFilename(extension) {
    const topic = (topicInput.value.trim() || "inkflow-blog")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "")
        .slice(0, 60);

    return `${topic || "inkflow-blog"}.${extension}`;
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
}


// -------------------- Blog statistics --------------------

function updateBlogStats(markdown, sources) {
    const articleText = markdown
        .replace(/\r\n/g, "\n")
        .replace(/\n## Sources[\s\S]*$/i, "");

    const plainText = articleText
        .replace(/```[\s\S]*?```/g, " ")
        .replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1")
        .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
        .replace(/[#>*_`~]/g, " ")
        .trim();

    const words = plainText.match(/\b[\w'-]+\b/g) || [];
    const wordCount = words.length;

    $("word-count").textContent = wordCount.toLocaleString();
    $("reading-time").textContent =
        `${Math.max(1, Math.ceil(wordCount / 200))} min`;
    $("source-count").textContent =
        Array.isArray(sources) ? sources.length : 0;
}

topicInput.addEventListener("input", () => {
    $("char-count").textContent = `${topicInput.value.length} / 300`;
});


// -------------------- Markdown preview --------------------

function renderInlineMarkdown(text) {
    let html = escapeHTML(text);

    html = html.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
        (_, label, url) =>
            `<a href="${escapeHTML(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`
    );

    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

    return html;
}

function renderMarkdown(markdown) {
    const lines = markdown.replace(/\r\n/g, "\n").split("\n");
    const output = [];

    let paragraph = [];
    let listType = null;
    let inCodeBlock = false;
    let codeLines = [];

    function flushParagraph() {
        if (paragraph.length) {
            output.push(
                `<p>${paragraph.map(renderInlineMarkdown).join("<br>")}</p>`
            );
            paragraph = [];
        }
    }

    function closeList() {
        if (listType) {
            output.push(`</${listType}>`);
            listType = null;
        }
    }

    for (const line of lines) {
        if (line.trim().startsWith("```")) {
            flushParagraph();
            closeList();

            if (inCodeBlock) {
                output.push(
                    `<pre><code>${escapeHTML(codeLines.join("\n"))}</code></pre>`
                );
                codeLines = [];
                inCodeBlock = false;
            } else {
                inCodeBlock = true;
            }
            continue;
        }

        if (inCodeBlock) {
            codeLines.push(line);
            continue;
        }

        const heading = line.match(/^(#{1,3})\s+(.+)$/);

        if (heading) {
            flushParagraph();
            closeList();

            const level = heading[1].length;
            output.push(
                `<h${level}>${renderInlineMarkdown(heading[2])}</h${level}>`
            );
            continue;
        }

        const unordered = line.match(/^\s*[-*]\s+(.+)$/);
        const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);

        if (unordered || ordered) {
            flushParagraph();

            const nextType = unordered ? "ul" : "ol";
            if (listType !== nextType) {
                closeList();
                output.push(`<${nextType}>`);
                listType = nextType;
            }

            const item = unordered ? unordered[1] : ordered[1];
            output.push(`<li>${renderInlineMarkdown(item)}</li>`);
            continue;
        }

        if (!line.trim()) {
            flushParagraph();
            closeList();
            continue;
        }

        closeList();
        paragraph.push(line);
    }

    flushParagraph();
    closeList();

    if (inCodeBlock) {
        output.push(
            `<pre><code>${escapeHTML(codeLines.join("\n"))}</code></pre>`
        );
    }

    return output.join("\n");
}


// -------------------- Progress tracking --------------------

function resetProgress() {
    completedWritingSections = 0;
    totalWritingSections = 5;

    for (const [name, step] of Object.entries(workflowSteps)) {
        if (!step) continue;

        step.classList.remove("active", "completed");

        const icon = step.querySelector(".workflow-step-icon");
        if (icon) {
            icon.textContent = String(workflowOrder.indexOf(name) + 1);
        }
    }

    progressPercentage.textContent = "0%";
    progressFill.style.width = "0%";
    progressTrack.setAttribute("aria-valuenow", "0");
}

function setLoading(isLoading) {
    generateBtn.disabled = isLoading;
    topicInput.disabled = isLoading;
    blogLengthInput.disabled = isLoading;
    writingToneInput.disabled = isLoading;
    targetAudienceInput.disabled = isLoading;

    buttonText.textContent = isLoading
        ? "Generating your blog..."
        : "Generate my blog";

    buttonIcon.textContent = isLoading ? "◌" : "✦";

    if (isLoading || currentBlog) {
        progressCard.classList.remove("hidden");
    } else {
        progressCard.classList.add("hidden");
    }
}

function updateProgress(stage, message, details = {}) {
    const titles = {
        starting: "Getting started",
        working: "AI workflow running",
        research: "Researching your topic",
        planning: "Planning your blog",
        writing: "Writing your blog",
        assembly: "Assembling your blog",
        proofreading: "Proofreading your blog",
        complete: "Your blog is ready!"
    };

    progressCard.classList.remove("hidden");
    progressTitle.textContent = titles[stage] || "Creating your blog...";
    progressMessage.textContent = message || "Please wait...";

    if (Number.isFinite(details.completed)) {
        completedWritingSections = details.completed;
    }

    if (Number.isFinite(details.total) && details.total > 0) {
        totalWritingSections = details.total;
    }

    let percent = stageProgress[stage] ?? 5;

    if (stage === "writing") {
        const ratio = Math.min(
            1,
            completedWritingSections / totalWritingSections
        );
        percent = Math.round(45 + ratio * 30);
    }

    percent = Math.max(0, Math.min(100, percent));
    progressPercentage.textContent = `${percent}%`;
    progressFill.style.width = `${percent}%`;
    progressTrack.setAttribute("aria-valuenow", String(percent));

    const currentIndex = workflowOrder.indexOf(stage);

    for (const [index, name] of workflowOrder.entries()) {
        const step = workflowSteps[name];
        if (!step) continue;

        step.classList.remove("active", "completed");
        const icon = step.querySelector(".workflow-step-icon");

        if (stage === "complete" || index < currentIndex) {
            step.classList.add("completed");
            if (icon) icon.textContent = "✓";
        } else if (index === currentIndex) {
            step.classList.add("active");
            if (icon) icon.textContent = String(index + 1);
        } else if (icon) {
            icon.textContent = String(index + 1);
        }
    }

    if (
        stage === "writing" &&
        completedWritingSections >= totalWritingSections
    ) {
        const step = workflowSteps.writing;
        if (step) {
            step.classList.remove("active");
            step.classList.add("completed");
            const icon = step.querySelector(".workflow-step-icon");
            if (icon) icon.textContent = "✓";
        }
    }
}


// -------------------- Research sources --------------------

function renderSources(sources) {
    sourcesList.replaceChildren();

    if (!Array.isArray(sources) || sources.length === 0) {
        sourcesCard.classList.add("hidden");
        return;
    }

    for (const source of sources) {
        if (!source || typeof source.url !== "string") continue;

        try {
            const parsedURL = new URL(source.url);
            if (!["http:", "https:"].includes(parsedURL.protocol)) continue;

            const item = document.createElement("div");
            item.className = "source-item";

            const link = document.createElement("a");
            link.className = "source-link";
            link.href = parsedURL.href;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = source.title || parsedURL.hostname;

            const description = document.createElement("p");
            description.textContent = parsedURL.hostname;

            item.append(link, description);
            sourcesList.appendChild(item);
        } catch {
            // Skip invalid source URLs.
        }
    }

    sourcesCard.classList.toggle(
        "hidden",
        sourcesList.children.length === 0
    );
}


// -------------------- Display blog --------------------

function displayBlog(data) {
    if (!data.success || typeof data.blog_markdown !== "string") {
        throw new Error("The server returned an unexpected response.");
    }

    currentBlog = data.blog_markdown;
    currentSources = Array.isArray(data.sources) ? data.sources : [];

    const displayText = currentBlog
        .replace(/\n## Sources[\s\S]*$/i, "")
        .trim();

    blogOutput.innerHTML = renderMarkdown(displayText);

    renderSources(currentSources);
    updateBlogStats(currentBlog, currentSources);

    resultSection.classList.remove("hidden");
    editPanel.classList.add("hidden");
    editToggleBtn.textContent = "Edit blog";

    revisionStatus.textContent =
        "Your current blog will be used as the starting point.";

    updateProgress("complete", "Your generated blog is displayed below.");

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// -------------------- Read streaming API events --------------------

async function readBlogStream(response) {
    if (!response.ok) {
        let message = "The server could not generate your blog.";

        try {
            const errorData = await response.json();
            if (typeof errorData.detail === "string") {
                message = errorData.detail;
            }
        } catch {
            // Use default error.
        }

        throw new Error(message);
    }

    if (!response.body) {
        throw new Error("Streaming is not supported by this response.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let receivedResult = false;

    function processEvent(eventText) {
        const dataLines = eventText
            .split(/\r?\n/)
            .filter((line) => line.startsWith("data:"))
            .map((line) => line.slice(5).trimStart());

        if (!dataLines.length) return;

        const payload = JSON.parse(dataLines.join("\n"));

        if (payload.event === "status") {
            updateProgress(payload.stage, payload.message, payload);
        } else if (payload.event === "result") {
            displayBlog(payload);
            receivedResult = true;
        } else if (payload.event === "error") {
            throw new Error(payload.message || "Blog generation failed.");
        }
    }

    try {
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const events = buffer.split(/\r?\n\r?\n/);
            buffer = events.pop() || "";

            for (const eventText of events) {
                if (eventText.trim()) processEvent(eventText);
            }
        }

        buffer += decoder.decode();
        if (buffer.trim()) processEvent(buffer);
    } finally {
        reader.releaseLock();
    }

    if (!receivedResult) {
        throw new Error(
            "The connection ended before the final blog was received. Please try again."
        );
    }
}


// -------------------- Generate blog --------------------

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const topic = topicInput.value.trim();
    clearError();
    resultSection.classList.add("hidden");

    if (topic.length < 3 || topic.length > 300) {
        showError("Please enter a topic between 3 and 300 characters.");
        topicInput.focus();
        return;
    }

    currentBlog = "";
    currentSources = [];
    resetProgress();
    setLoading(true);

    updateProgress("starting", "Preparing your blog request...");

    try {
        const response = await fetch(`${API_URL}/generate/stream`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            body: JSON.stringify({
                topic,
                blog_length: blogLengthInput.value,
                writing_tone: writingToneInput.value,
                target_audience: targetAudienceInput.value
            })
        });

        await readBlogStream(response);
    } catch (error) {
        console.error("Blog generation error:", error);

        showError(error instanceof TypeError
            ? "Could not connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
            : (error.message || "Something went wrong. Please try again."));
    } finally {
        setLoading(false);
    }
});


// -------------------- Copy blog --------------------

copyBtn.addEventListener("click", async () => {
    if (!currentBlog) {
        showError("Generate a blog before copying it.");
        return;
    }

    try {
        await navigator.clipboard.writeText(currentBlog);
        copyBtn.textContent = "Copied!";

        setTimeout(() => {
            copyBtn.textContent = "Copy blog";
        }, 1800);
    } catch {
        showError(
            "Clipboard access failed. You can select and copy the blog text manually."
        );
    }
});


// -------------------- Markdown export --------------------

downloadBtn.addEventListener("click", () => {
    if (!currentBlog) {
        showError("Generate a blog before exporting it.");
        return;
    }

    const blob = new Blob([currentBlog], {
        type: "text/markdown;charset=utf-8"
    });

    downloadBlob(blob, getExportFilename("md"));
    clearError();
});


// Convert Markdown to readable plain text for PDF and Word.
function markdownToExportLines(markdown) {
    return markdown.replace(/\r\n/g, "\n").split("\n").map((line) => {
        let text = line;
        text = text.replace(/^#{1,6}\s+/, "");
        text = text.replace(/^\s*[-*]\s+/, "• ");
        text = text.replace(/^\s*\d+[.)]\s+/, "• ");
        text = text.replace(
            /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
            "$1 ($2)"
        );
        text = text.replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1");
        text = text.replace(/```/g, "");
        text = text.replace(/(\*\*|__)(.*?)\1/g, "$2");
        text = text.replace(/(\*|_)(.*?)\1/g, "$2");
        text = text.replace(/`([^`]+)`/g, "$1");
        return text;
    });
}


// -------------------- PDF export --------------------

exportPdfBtn.addEventListener("click", () => {
    if (!currentBlog) {
        showError("Generate a blog before exporting it.");
        return;
    }

    if (!window.jspdf || !window.jspdf.jsPDF) {
        showError(
            "PDF library did not load. Check your internet connection and refresh the page."
        );
        return;
    }

    try {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF({ unit: "pt", format: "a4" });
        const margin = 48;
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const maxWidth = pageWidth - margin * 2;
        let y = margin;

        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(11);

        for (const rawLine of markdownToExportLines(currentBlog)) {
            const line = rawLine.trimEnd();

            if (!line.trim()) {
                y += 8;
                if (y > pageHeight - margin) {
                    pdf.addPage();
                    y = margin;
                }
                continue;
            }

            const wrappedLines = pdf.splitTextToSize(line, maxWidth);

            for (const wrappedLine of wrappedLines) {
                if (y > pageHeight - margin) {
                    pdf.addPage();
                    y = margin;
                }

                pdf.text(wrappedLine, margin, y);
                y += 15;
            }
        }

        pdf.save(getExportFilename("pdf"));
        clearError();
    } catch (error) {
        console.error("PDF export error:", error);
        showError("PDF export failed. Please try again.");
    }
});


// -------------------- Word DOCX export --------------------


exportDocxBtn.addEventListener("click", async () => {
    if (!currentBlog) {
        showError("Generate a blog before exporting it.");
        return;
    }

    const originalText = exportDocxBtn.textContent;
    exportDocxBtn.disabled = true;
    exportDocxBtn.textContent = "Preparing Word...";
    clearError();

    try {
        const response = await fetch(`${API_URL}/export/docx`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            },
            body: JSON.stringify({
                topic: topicInput.value.trim() || "InkFlow AI Blog",
                blog_markdown: currentBlog
            })
        });

        if (!response.ok) {
            let message = "Word export failed.";

            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    message = typeof errorData.detail === "string"
                        ? errorData.detail
                        : JSON.stringify(errorData.detail);
                }
            } catch {
                // Use the default error message.
            }

            throw new Error(message);
        }

        const blob = await response.blob();

        if (blob.size < 1000) {
            throw new Error(
                "The Word document appears incomplete. Please try again."
            );
        }

        const wordBlob = new Blob([await blob.arrayBuffer()], {
            type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        });

        const disposition = response.headers.get("Content-Disposition");
        const filenameMatch = disposition &&
            disposition.match(/filename="?([^";]+)"?/i);

        const filename = filenameMatch
            ? filenameMatch[1]
            : getExportFilename("docx");

        downloadBlob(wordBlob, filename);
        clearError();

    } catch (error) {
        console.error("Word export error:", error);

        showError(
            error instanceof TypeError
                ? "Could not connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
                : (error.message || "Word export failed. Please try again.")
        );

    } finally {
        exportDocxBtn.disabled = false;
        exportDocxBtn.textContent = originalText;
    }
});


// -------------------- Manual blog editing --------------------

editToggleBtn.addEventListener("click", () => {
    if (!currentBlog) {
        showError("Generate a blog before editing it.");
        return;
    }

    const opening = editPanel.classList.contains("hidden");

    if (opening) {
        blogEditor.value = currentBlog;
        editPanel.classList.remove("hidden");
        editToggleBtn.textContent = "Close editor";
        blogEditor.focus();
    } else {
        editPanel.classList.add("hidden");
        editToggleBtn.textContent = "Edit blog";
    }
});

applyEditBtn.addEventListener("click", () => {
    const editedBlog = blogEditor.value.trim();

    if (editedBlog.length < 20) {
        showError("The blog is too short. Please keep at least 20 characters.");
        blogEditor.focus();
        return;
    }

    currentBlog = editedBlog;
    blogOutput.innerHTML = renderMarkdown(
        currentBlog.replace(/\n## Sources[\s\S]*$/i, "").trim()
    );

    updateBlogStats(currentBlog, currentSources);
    editPanel.classList.add("hidden");
    editToggleBtn.textContent = "Edit blog";
    clearError();

    revisionStatus.textContent =
        "Your manual edits have been applied. You can refine this version further.";
});

cancelEditBtn.addEventListener("click", () => {
    editPanel.classList.add("hidden");
    editToggleBtn.textContent = "Edit blog";
});


// -------------------- Gemini regeneration --------------------

regenerateBtn.addEventListener("click", async () => {
    if (!currentBlog) {
        showError("Generate a blog before regenerating it.");
        return;
    }

    const instructions = revisionInstructions.value.trim();

    if (instructions.length < 3) {
        showError(
            "Please describe the changes you want in at least 3 characters."
        );
        revisionInstructions.focus();
        return;
    }

    clearError();
    regenerateBtn.disabled = true;
    editToggleBtn.disabled = true;
    regenerateButtonText.textContent = "Regenerating...";
    revisionStatus.textContent = "Gemini is revising your blog. Please wait...";

    try {
        const response = await fetch(`${API_URL}/regenerate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                topic: topicInput.value.trim() || "Blog topic",
                blog_markdown: currentBlog,
                instructions
            })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                data.detail || "Could not regenerate the blog. Please try again."
            );
        }

        if (
            !data.success ||
            typeof data.blog_markdown !== "string" ||
            !data.blog_markdown.trim()
        ) {
            throw new Error("The server returned an unexpected revision response.");
        }

        currentBlog = data.blog_markdown;

        blogOutput.innerHTML = renderMarkdown(
            currentBlog.replace(/\n## Sources[\s\S]*$/i, "").trim()
        );

        updateBlogStats(currentBlog, currentSources);
        revisionInstructions.value = "";
        revisionStatus.textContent =
            "Blog revised successfully. You can edit it again or request another revision.";

        resultSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    } catch (error) {
        console.error("Blog revision error:", error);

        showError(error instanceof TypeError
            ? "Could not connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
            : (error.message || "Something went wrong while revising the blog."));

        revisionStatus.textContent =
            "Revision did not complete. Your previous blog is still available.";
    } finally {
        regenerateBtn.disabled = false;
        editToggleBtn.disabled = false;
        regenerateButtonText.textContent = "Regenerate blog";
    }
});

console.log("InkFlow AI initialized with editing and all export options.");