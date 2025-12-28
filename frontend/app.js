/**
 * RAGMind Web Frontend
 * Main Application Logic
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';

// Translations
const i18n = {
    ar: {
        nav_dashboard: "لوحة التحكم",
        nav_projects: "المشاريع",
        nav_chat: "المحادثة الذكية",
        nav_bot: "إعدادات البوت",
        stat_projects: "إجمالي المشاريع",
        stat_docs: "المستندات",
        stat_chunks: "القطع النصية",
        recent_projects: "المشاريع الأخيرة",
        view_all: "عرض الكل",
        your_projects: "مشاريعك",
        welcome_title: "مرحباً بك في RAGMind",
        project_name_ph: "مثلاً: أبحاث الذكاء الاصطناعي",
        project_desc_ph: "وصف مختصر للمشروع...",
        create_project_btn: "إنشاء المشروع",
        upload_title: "رفع مستندات جديدة",
        upload_desc: "اسحب الملفات هنا أو اضغط للاختيار",
        docs_title: "المستندات الحالية",
        bot_settings_title: "إعدادات بوت التليجرام",
        bot_active_project: "المشروع النشط",
        bot_active_project_desc: "اختر المشروع الذي سيقوم البوت بالإجابة منه.",
        save_settings: "حفظ الإعدادات",
        bot_profile: "ملف البوت",
        bot_profile_desc: "تحديث اسم البوت على تليجرام.",
        bot_name: "اسم البوت",
        update_profile: "تحديث الملف الشخصي",
        select_project_ph: "اختر مشروعاً...",
        delete_confirm: "هل أنت متأكد؟",
        success_saved: "تم الحفظ بنجاح",
        error_generic: "حدث خطأ ما"
    },
    en: {
        nav_dashboard: "Dashboard",
        nav_projects: "Projects",
        nav_chat: "Smart Chat",
        nav_bot: "Bot Settings",
        stat_projects: "Total Projects",
        stat_docs: "Documents",
        stat_chunks: "Text Chunks",
        recent_projects: "Recent Projects",
        view_all: "View All",
        your_projects: "Your Projects",
        welcome_title: "Welcome to RAGMind",
        project_name_ph: "Ex: AI Research",
        project_desc_ph: "Short description...",
        create_project_btn: "Create Project",
        upload_title: "Upload New Documents",
        upload_desc: "Drag files here or click to select",
        docs_title: "Current Documents",
        bot_settings_title: "Telegram Bot Settings",
        bot_active_project: "Active Project",
        bot_active_project_desc: "Select the project the bot will answer from.",
        save_settings: "Save Settings",
        bot_profile: "Bot Profile",
        bot_profile_desc: "Update Bot Name on Telegram.",
        bot_name: "Bot Name",
        update_profile: "Update Profile",
        select_project_ph: "Select a project...",
        delete_confirm: "Are you sure?",
        success_saved: "Saved successfully",
        error_generic: "Something went wrong"
    }
};

// State Management
const state = {
    currentView: 'dashboard',
    projects: [],
    stats: null,
    selectedProject: null,
    chatMessages: [],
    isUploading: false,
    lang: localStorage.getItem('lang') || 'ar',
    theme: localStorage.getItem('theme') || 'dark'
};

// DOM Elements
const elements = {
    viewContainer: document.getElementById('view-container'),
    navItems: document.querySelectorAll('.sidebar-nav li'),
    newProjectBtn: document.getElementById('new-project-btn'),
    modalOverlay: document.getElementById('modal-overlay'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    closeModalBtn: document.querySelector('.close-modal'),
    themeToggle: document.getElementById('theme-toggle'),
    langToggle: document.getElementById('lang-toggle')
};

// --- API Client ---

const api = {
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`API Get Error (${endpoint}):`, error);
            showNotification(state.lang === 'ar' ? 'خطأ في الاتصال بالسيرفر' : 'Server Connection Error', 'error');
            throw error;
        }
    },

    async post(endpoint, data, isFormData = false) {
        try {
            const options = {
                method: 'POST',
                body: isFormData ? data : JSON.stringify(data)
            };
            if (!isFormData) {
                options.headers = { 'Content-Type': 'application/json' };
            }

            const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error');
            }
            return await response.json();
        } catch (error) {
            console.error(`API Post Error (${endpoint}):`, error);
            showNotification(error.message, 'error');
            throw error;
        }
    },

    async delete(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, { method: 'DELETE' });
            if (!response.ok) throw new Error('Delete failed');
            return true;
        } catch (error) {
            console.error(`API Delete Error (${endpoint}):`, error);
            showNotification(error.message, 'error');
            throw error;
        }
    }
};

// --- View Rendering ---

const views = {
    async dashboard() {
        renderTemplate('dashboard-template');
        showLoader();

        try {
            const [projects, stats] = await Promise.all([
                api.get('/projects/'),
                api.get('/stats/')
            ]);
            state.projects = projects;

            // Update stats
            document.getElementById('stat-projects').textContent = stats.projects;
            document.getElementById('stat-docs').textContent = stats.documents;
            document.getElementById('stat-chunks').textContent = stats.chunks;

            // Render recent projects
            const list = document.getElementById('recent-projects-list');
            list.innerHTML = '';
            projects.slice(0, 3).forEach(project => {
                list.appendChild(createProjectCard(project));
            });

            applyTranslations();
        } catch (error) {
            console.error('Dashboard Load Error:', error);
        } finally {
            hideLoader();
        }
    },

    async projects() {
        renderTemplate('projects-template');
        showLoader();

        try {
            const projects = await api.get('/projects/');
            state.projects = projects;

            const list = document.getElementById('all-projects-list');
            list.innerHTML = '';
            projects.forEach(project => {
                list.appendChild(createProjectCard(project));
            });
            applyTranslations();
        } catch (error) {
            console.error('Projects Load Error:', error);
        } finally {
            hideLoader();
        }
    },

    async projectDetail(projectId) {
        renderTemplate('project-detail-template');
        showLoader();

        try {
            const project = await api.get(`/projects/${projectId}`);
            const docs = await api.get(`/projects/${projectId}/documents`);

            state.selectedProject = project;

            document.getElementById('project-name-title').textContent = project.name;

            const docsList = document.getElementById('project-docs-list');
            docsList.innerHTML = '';

            if (docs.length === 0) {
                docsList.innerHTML = `<p class="empty-msg">${state.lang === 'ar' ? 'لا توجد مستندات بعد' : 'No documents yet'}</p>`;
            } else {
                docs.forEach(doc => {
                    docsList.appendChild(createDocItem(doc));
                });
            }

            // Setup Upload Zone
            setupUploadZone(projectId);

            document.getElementById('back-to-projects').onclick = () => switchView('projects');
            applyTranslations();
        } catch (error) {
            console.error('Project Detail Load Error:', error);
        } finally {
            hideLoader();
        }
    },

    async chat() {
        renderTemplate('chat-template');

        const select = document.getElementById('chat-project-select');
        const projects = await api.get('/projects/');

        projects.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.name;
            select.appendChild(opt);
        });

        const sendBtn = document.getElementById('send-btn');
        const chatInput = document.getElementById('chat-input');

        sendBtn.onclick = handleChatSubmit;
        chatInput.onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleChatSubmit();
            }
        };
        applyTranslations();
    },

    async 'bot-config'() {
        renderTemplate('bot-config-template');
        showLoader();

        try {
            const [projects, config] = await Promise.all([
                api.get('/projects/'),
                api.get('/bot/config')
            ]);

            const select = document.getElementById('bot-active-project');
            projects.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name;
                if (config.active_project_id == p.id) opt.selected = true;
                select.appendChild(opt);
            });

            document.getElementById('save-bot-config-btn').onclick = async () => {
                const projectId = select.value;
                if (!projectId) return;
                try {
                    await api.post('/bot/config', { active_project_id: parseInt(projectId) });
                    showNotification(i18n[state.lang].success_saved, 'success');
                } catch (e) {
                    console.error(e);
                }
            };

            document.getElementById('update-bot-profile-btn').onclick = async () => {
                const name = document.getElementById('bot-name-input').value;
                if (!name) return;
                const formData = new FormData();
                formData.append('name', name);
                try {
                    await api.post('/bot/profile', formData, true);
                    showNotification(i18n[state.lang].success_saved, 'success');
                } catch (e) {
                    console.error(e);
                }
            };

            applyTranslations();
        } catch (error) {
            console.error('Bot Config Error:', error);
        } finally {
            hideLoader();
        }
    }
};

// --- Helpers ---

function renderTemplate(templateId) {
    const template = document.getElementById(templateId);
    const clone = template.content.cloneNode(true);
    elements.viewContainer.innerHTML = '';
    elements.viewContainer.appendChild(clone);
}

function showLoader() {
    const loader = document.createElement('div');
    loader.className = 'loader-container';
    loader.innerHTML = '<div class="loader"></div>';
    elements.viewContainer.appendChild(loader);
}

function hideLoader() {
    const loader = elements.viewContainer.querySelector('.loader-container');
    if (loader) loader.remove();
}

function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'project-card';
    card.innerHTML = `
        <h3>${project.name}</h3>
        <p>${project.description || (state.lang === 'ar' ? 'لا يوجد وصف' : 'No description')}</p>
        <div class="project-meta">
            <span><i class="far fa-calendar"></i> ${new Date(project.created_at).toLocaleDateString(state.lang === 'ar' ? 'ar-EG' : 'en-US')}</span>
            <button class="delete-project-btn" data-id="${project.id}"><i class="fas fa-trash"></i></button>
        </div>
    `;

    card.onclick = (e) => {
        if (e.target.closest('.delete-project-btn')) {
            handleDeleteProject(project.id);
            return;
        }
        switchView('projectDetail', project.id);
    };

    return card;
}

function createDocItem(doc) {
    const item = document.createElement('div');
    item.className = 'doc-item';
    const statusClass = doc.status === 'completed' ? 'status-done' : (doc.status === 'failed' ? 'status-error' : 'status-processing');
    const statusIcon = doc.status === 'completed' ? 'fa-check-circle' : (doc.status === 'failed' ? 'fa-exclamation-circle' : 'fa-spinner fa-spin');

    const statusText = {
        completed: state.lang === 'ar' ? 'مكتمل' : 'Completed',
        failed: state.lang === 'ar' ? 'فشل' : 'Failed',
        processing: state.lang === 'ar' ? 'جاري المعالجة' : 'Processing'
    };

    item.innerHTML = `
        <div class="doc-info">
            <i class="fas fa-file-pdf"></i>
            <div class="doc-details">
                <span class="doc-name">${doc.original_filename}</span>
                <span class="doc-size">${(doc.file_size / 1024).toFixed(1)} KB</span>
            </div>
        </div>
        <div class="doc-status ${statusClass}">
            <i class="fas ${statusIcon}"></i>
            <span>${statusText[doc.status] || doc.status}</span>
        </div>
        <button class="delete-doc-btn" data-id="${doc.id}"><i class="fas fa-trash"></i></button>
    `;

    item.querySelector('.delete-doc-btn').onclick = () => handleDeleteDoc(doc.id);

    return item;
}

function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function applyTranslations() {
    const t = i18n[state.lang];
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        if (t[key]) el.textContent = t[key];
    });

    // Update placeholders
    if (document.getElementById('new-project-name')) {
        document.getElementById('new-project-name').placeholder = t.project_name_ph;
        document.getElementById('new-project-desc').placeholder = t.project_desc_ph;
    }

    // Update Lang Button
    elements.langToggle.querySelector('.lang-code').textContent = state.lang === 'ar' ? 'EN' : 'AR';

    // Update Dir
    document.documentElement.dir = state.lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = state.lang;
}

function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.body.classList.toggle('light-theme', state.theme === 'light');
    document.body.classList.toggle('dark-theme', state.theme === 'dark');

    const icon = elements.themeToggle.querySelector('i');
    icon.className = state.theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';

    localStorage.setItem('theme', state.theme);
}

function toggleLang() {
    state.lang = state.lang === 'ar' ? 'en' : 'ar';
    localStorage.setItem('lang', state.lang);
    applyTranslations();
    switchView(state.currentView, state.selectedProject ? state.selectedProject.id : null);
}

// --- Event Handlers ---

async function switchView(viewName, params = null) {
    state.currentView = viewName;

    // Update Nav
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.view === viewName);
    });

    // Render View
    if (viewName === 'projectDetail') {
        await views.projectDetail(params);
    } else if (views[viewName]) {
        await views[viewName]();
    }
}

async function handleNewProject() {
    elements.modalTitle.textContent = i18n[state.lang].create_project_btn;
    elements.modalBody.innerHTML = `
        <div class="form-group">
            <label>${state.lang === 'ar' ? 'اسم المشروع' : 'Project Name'}</label>
            <input type="text" id="new-project-name" class="form-control">
        </div>
        <div class="form-group">
            <label>${state.lang === 'ar' ? 'الوصف' : 'Description'}</label>
            <textarea id="new-project-desc" class="form-control"></textarea>
        </div>
        <button id="save-project-btn" class="btn btn-primary w-100 mt-4">${i18n[state.lang].create_project_btn}</button>
    `;
    applyTranslations();

    elements.modalOverlay.classList.remove('hidden');

    document.getElementById('save-project-btn').onclick = async () => {
        const name = document.getElementById('new-project-name').value;
        const description = document.getElementById('new-project-desc').value;

        if (!name) {
            showNotification(state.lang === 'ar' ? 'يرجى إدخال اسم المشروع' : 'Please enter project name', 'warning');
            return;
        }

        try {
            await api.post('/projects/', { name, description });
            showNotification(i18n[state.lang].success_saved, 'success');
            elements.modalOverlay.classList.add('hidden');
            switchView(state.currentView); // Refresh current view
        } catch (error) {
            console.error('Create Project Error:', error);
        }
    };
}

async function handleDeleteProject(id) {
    if (confirm(i18n[state.lang].delete_confirm)) {
        try {
            await api.delete(`/projects/${id}`);
            showNotification(i18n[state.lang].success_saved, 'success');
            switchView(state.currentView);
        } catch (error) {
            console.error('Delete Project Error:', error);
        }
    }
}

async function handleDeleteDoc(id) {
    if (confirm(i18n[state.lang].delete_confirm)) {
        try {
            await api.delete(`/documents/${id}`);
            showNotification(i18n[state.lang].success_saved, 'success');
            if (state.selectedProject) {
                switchView('projectDetail', state.selectedProject.id);
            }
        } catch (error) {
            console.error('Delete Doc Error:', error);
        }
    }
}

async function handleChatSubmit() {
    const input = document.getElementById('chat-input');
    const projectSelect = document.getElementById('chat-project-select');
    const langSelect = document.getElementById('chat-lang');

    const query = input.value.trim();
    const projectId = projectSelect.value;
    const language = langSelect.value;

    if (!query) return;
    if (!projectId) {
        showNotification(state.lang === 'ar' ? 'يرجى اختيار مشروع أولاً' : 'Select a project first', 'warning');
        return;
    }

    addChatMessage('user', query);
    input.value = '';

    const thinkingId = addChatMessage('bot', state.lang === 'ar' ? 'جاري التفكير...' : 'Thinking...', true);

    try {
        const result = await api.post(`/projects/${projectId}/query`, {
            query,
            language,
            top_k: 5
        });

        updateChatMessage(thinkingId, result.answer, result.sources);
    } catch (error) {
        updateChatMessage(thinkingId, i18n[state.lang].error_generic);
    }
}

function addChatMessage(role, text, isThinking = false) {
    const messagesContainer = document.getElementById('chat-messages');
    const welcome = messagesContainer.querySelector('.welcome-msg');
    if (welcome) welcome.remove();

    const id = Date.now();
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${role}-msg`;
    msgDiv.id = `msg-${id}`;
    msgDiv.innerHTML = `
        <div class="msg-avatar">${role === 'user' ? 'U' : '<i class="fas fa-robot"></i>'}</div>
        <div class="msg-content">
            <div class="text">${text}</div>
            ${isThinking ? '<div class="typing-indicator"><span></span><span></span><span></span></div>' : ''}
        </div>
    `;
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return id;
}

function updateChatMessage(id, text, sources = null) {
    const msgDiv = document.getElementById(`msg-${id}`);
    if (!msgDiv) return;

    const content = msgDiv.querySelector('.text');
    const indicator = msgDiv.querySelector('.typing-indicator');
    if (indicator) indicator.remove();

    content.textContent = text;

    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'msg-sources';
        sourcesDiv.innerHTML = `<strong>${state.lang === 'ar' ? 'المصادر:' : 'Sources:'}</strong>`;
        const list = document.createElement('ul');
        sources.slice(0, 3).forEach(s => {
            const li = document.createElement('li');
            li.textContent = `${s.document_name} (${(s.similarity * 100).toFixed(1)}%)`;
            list.appendChild(li);
        });
        sourcesDiv.appendChild(list);
        msgDiv.querySelector('.msg-content').appendChild(sourcesDiv);
    }

    const container = document.getElementById('chat-messages');
    container.scrollTop = container.scrollHeight;
}

function setupUploadZone(projectId) {
    const zone = document.getElementById('upload-zone');
    const input = document.getElementById('file-input');

    zone.onclick = () => input.click();

    zone.ondragover = (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    };

    zone.ondragleave = () => zone.classList.remove('dragover');

    zone.ondrop = (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files, projectId);
    };

    input.onchange = () => handleFiles(input.files, projectId);
}

async function handleFiles(files, projectId) {
    for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);

        showNotification(`${state.lang === 'ar' ? 'جاري رفع' : 'Uploading'} ${file.name}...`, 'info');

        try {
            await api.post(`/projects/${projectId}/documents`, formData, true);
            showNotification(`${state.lang === 'ar' ? 'تم رفع' : 'Uploaded'} ${file.name}`, 'success');
            switchView('projectDetail', projectId); // Refresh list
        } catch (error) {
            console.error('Upload Error:', error);
        }
    }
}

// --- Initialization ---

document.addEventListener('DOMContentLoaded', () => {
    // Nav Clicks
    elements.navItems.forEach(item => {
        item.onclick = () => switchView(item.dataset.view);
    });

    // New Project Click
    elements.newProjectBtn.onclick = handleNewProject;

    // Close Modal
    elements.closeModalBtn.onclick = () => elements.modalOverlay.classList.add('hidden');
    elements.modalOverlay.onclick = (e) => {
        if (e.target === elements.modalOverlay) elements.modalOverlay.classList.add('hidden');
    };

    // Theme & Lang
    elements.themeToggle.onclick = toggleTheme;
    elements.langToggle.onclick = toggleLang;

    // Init State
    if (state.theme === 'light') {
        document.body.classList.add('light-theme');
        document.body.classList.remove('dark-theme');
        elements.themeToggle.querySelector('i').className = 'fas fa-sun';
    }

    // Initial View
    applyTranslations();
    switchView('dashboard');
});
