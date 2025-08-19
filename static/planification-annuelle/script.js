document.addEventListener('DOMContentLoaded', function() {
    // Référence au template de cours
    const courseTemplate = document.getElementById('course-template');
    courseTemplate.remove(); // Retire le template du DOM
    courseTemplate.id = ''; // Retire l'ID pour éviter les duplications

    // Gestionnaire pour le changement de logo
    const logoUpload = document.getElementById('logo-upload');
    const schoolLogo = document.getElementById('school-logo');
    const changeLogoBtn = document.getElementById('change-logo');
    
    // Références aux champs d'information de l'enseignant et de la classe
    const teacherNameInput = document.getElementById('teacher-name');
    const classNameInput = document.getElementById('class-name');

    changeLogoBtn.addEventListener('click', function() {
        logoUpload.click();
    });

    logoUpload.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function(event) {
                schoolLogo.src = event.target.result;
                // Sauvegarder le logo dans le localStorage
                localStorage.setItem('schoolLogo', event.target.result);
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    });

    // Charger le logo s'il existe dans le localStorage
    const savedLogo = localStorage.getItem('schoolLogo');
    if (savedLogo) {
        schoolLogo.src = savedLogo;
    }
    
    // Gestionnaires pour sauvegarder les informations de l'enseignant et de la classe
    teacherNameInput.addEventListener('change', function() {
        localStorage.setItem('teacherName', teacherNameInput.value);
    });
    
    classNameInput.addEventListener('change', function() {
        localStorage.setItem('className', classNameInput.value);
    });
    
    // Charger les informations de l'enseignant et de la classe si elles existent
    const savedTeacherName = localStorage.getItem('teacherName');
    if (savedTeacherName) {
        teacherNameInput.value = savedTeacherName;
    }
    
    const savedClassName = localStorage.getItem('className');
    if (savedClassName) {
        classNameInput.value = savedClassName;
    }

    // Ajouter un nouveau cours
    const addCourseBtn = document.getElementById('add-course');
    addCourseBtn.addEventListener('click', function() {
        addNewCourse();
    });

    // Fonction pour ajouter un nouveau cours
    function addNewCourse() {
        const planningContainer = document.getElementById('planning-container');
        const newCourse = courseTemplate.cloneNode(true);
        
        // Ajouter des gestionnaires d'événements pour ce cours
        setupCourseEventListeners(newCourse);
        
        // Ajouter une première partie et une première leçon
        addPartToCourse(newCourse, 'PÉRIODE 1');
        addRowToCourse(newCourse);
        
        planningContainer.appendChild(newCourse);
    }

    // Configuration des gestionnaires d'événements pour un cours
    function setupCourseEventListeners(courseElement) {
        const addRowBtn = courseElement.querySelector('.add-row');
        const addPartBtn = courseElement.querySelector('.add-part');
        const removeCourseBtn = courseElement.querySelector('.remove-course');

        addRowBtn.addEventListener('click', function() {
            addRowToCourse(courseElement);
        });

        addPartBtn.addEventListener('click', function() {
            const partCount = courseElement.querySelectorAll('.part-row').length + 1;
            addPartToCourse(courseElement, `PÉRIODE ${partCount}`);
        });

        removeCourseBtn.addEventListener('click', function() {
            if (confirm('Êtes-vous sûr de vouloir supprimer ce cours?')) {
                courseElement.remove();
            }
        });
    }

    // Ajouter une partie à un cours
    function addPartToCourse(courseElement, partTitle) {
        const tbody = courseElement.querySelector('tbody');
        const partRow = document.createElement('tr');
        partRow.className = 'part-row';
        
        const partCell = document.createElement('td');
        partCell.colSpan = 9; // Couvre toutes les colonnes
        partCell.textContent = partTitle;
        partCell.className = 'part-header';
        
        partRow.appendChild(partCell);
        tbody.appendChild(partRow);
    }

    // Ajouter une ligne (leçon) à un cours
    function addRowToCourse(courseElement) {
        const tbody = courseElement.querySelector('tbody');
        const newRow = document.createElement('tr');
        
        // Créer les cellules
        const columns = [
            { type: 'text', placeholder: 'Numéro' },
            { type: 'text', placeholder: 'Durée' },
            { type: 'text', placeholder: 'Objectif principal' },
            { type: 'text', placeholder: 'Objectifs spécifiques' },
            { type: 'text', placeholder: 'Niveau' },
            { type: 'text', placeholder: 'Lignes' },
            { type: 'checkbox' },
            { type: 'task', placeholder: 'Tâche/Devoir' },
            { type: 'text', placeholder: 'Remarques' }
        ];

        columns.forEach(column => {
            const cell = document.createElement('td');
            
            if (column.type === 'checkbox') {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'completed-checkbox';
                cell.className = 'checkbox-cell';
                cell.appendChild(checkbox);
            } else if (column.type === 'task') {
                // Créer un conteneur pour les contrôles de tâche
                const taskContainer = document.createElement('div');
                taskContainer.className = 'task-container';
                
                // Champ de texte pour la tâche
                const taskInput = document.createElement('input');
                taskInput.type = 'text';
                taskInput.placeholder = column.placeholder;
                taskInput.className = 'task-input';
                
                // Boutons pour ajouter un PDF ou un lien
                const buttonContainer = document.createElement('div');
                buttonContainer.className = 'task-buttons';
                
                // Bouton pour ajouter un lien
                const addLinkBtn = document.createElement('button');
                addLinkBtn.type = 'button';
                addLinkBtn.className = 'task-btn link-btn';
                addLinkBtn.innerHTML = '<i class="fa">🔗</i>';
                addLinkBtn.title = 'Ajouter un lien';
                addLinkBtn.onclick = function() {
                    const url = prompt('Entrez l\'URL du lien:');
                    if (url) {
                        const linkText = prompt('Entrez le texte à afficher pour ce lien:', 'Voir le document');
                        const link = document.createElement('a');
                        link.href = url;
                        link.target = '_blank';
                        link.textContent = linkText || 'Voir le document';
                        link.className = 'task-link';
                        
                        // Remplacer l'input par le lien
                        if (taskContainer.contains(taskInput)) {
                            taskContainer.replaceChild(link, taskInput);
                        } else {
                            taskContainer.appendChild(link);
                        }
                    }
                };
                
                // Bouton pour ajouter un PDF
                const addPdfBtn = document.createElement('button');
                addPdfBtn.type = 'button';
                addPdfBtn.className = 'task-btn pdf-btn';
                addPdfBtn.innerHTML = '<i class="fa">📄</i>';
                addPdfBtn.title = 'Ajouter un PDF';
                
                // Input caché pour le téléchargement de fichier
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = '.pdf';
                fileInput.style.display = 'none';
                fileInput.onchange = function(e) {
                    if (e.target.files && e.target.files[0]) {
                        const file = e.target.files[0];
                        const reader = new FileReader();
                        reader.onload = function(event) {
                            // Créer un lien vers le PDF
                            const pdfLink = document.createElement('a');
                            pdfLink.href = event.target.result;
                            pdfLink.target = '_blank';
                            pdfLink.textContent = file.name;
                            pdfLink.className = 'task-link pdf-link';
                            pdfLink.download = file.name;
                            
                            // Remplacer l'input par le lien PDF
                            if (taskContainer.contains(taskInput)) {
                                taskContainer.replaceChild(pdfLink, taskInput);
                            } else {
                                taskContainer.appendChild(pdfLink);
                            }
                            
                            // Stocker le PDF dans localStorage (attention à la taille)
                            try {
                                localStorage.setItem('pdf_' + Date.now(), event.target.result);
                            } catch (e) {
                                console.warn('Le PDF est trop volumineux pour être stocké localement');
                            }
                        };
                        reader.readAsDataURL(file);
                    }
                };
                
                addPdfBtn.onclick = function() {
                    fileInput.click();
                };
                
                // Assembler les éléments
                buttonContainer.appendChild(addLinkBtn);
                buttonContainer.appendChild(addPdfBtn);
                taskContainer.appendChild(taskInput);
                taskContainer.appendChild(buttonContainer);
                taskContainer.appendChild(fileInput);
                
                cell.appendChild(taskContainer);
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.placeholder = column.placeholder;
                cell.appendChild(input);
            }
            
            newRow.appendChild(cell);
        });
        
        tbody.appendChild(newRow);
    }

    // Exportation en PDF
    const printPdfBtn = document.getElementById('print-pdf');
    printPdfBtn.addEventListener('click', async function() {
        // Utiliser html2canvas et jsPDF pour générer un PDF
        const { jsPDF } = window.jspdf;
        
        const planningContainer = document.getElementById('planning-container');
        const coursePlanning = planningContainer.querySelectorAll('.course-planning');
        
        if (coursePlanning.length === 0) {
            alert('Veuillez ajouter au moins un cours avant d\'exporter en PDF.');
            return;
        }

        // Créer un nouveau document PDF
        const doc = new jsPDF('l', 'mm', 'a4'); // landscape orientation
        let pageHeight = doc.internal.pageSize.height;
        let pageWidth = doc.internal.pageSize.width;
        let yPosition = 20;

        // Ajouter le logo et le titre
        const logo = document.getElementById('school-logo');
        if (logo.src !== window.location.href) {
            doc.addImage(logo.src, 'PNG', 20, yPosition, 30, 15);
        }
        
        doc.setFontSize(18);
        doc.text('Planification Annuelle', pageWidth / 2, yPosition + 10, { align: 'center' });
        yPosition += 25;
        
        // Ajouter les informations de l'enseignant et de la classe
        const teacherName = document.getElementById('teacher-name').value;
        const className = document.getElementById('class-name').value;
        
        // Ajouter un rectangle de fond pour les informations
        doc.setFillColor(240, 240, 240);
        doc.rect(15, yPosition - 5, pageWidth - 30, 15, 'F');
        
        // Ajouter les informations avec une mise en forme améliorée
        doc.setFontSize(12);
        doc.setTextColor(40, 40, 40);
        doc.setFont(undefined, 'bold');
        
        doc.text('Enseignant(e):', 20, yPosition + 3);
        doc.setFont(undefined, 'normal');
        doc.text(teacherName || '___________________', 70, yPosition + 3);
        
        doc.setFont(undefined, 'bold');
        doc.text('Classe:', pageWidth / 2 + 20, yPosition + 3);
        doc.setFont(undefined, 'normal');
        doc.text(className || '___________________', pageWidth / 2 + 55, yPosition + 3);
        
        yPosition += 20; // Augmenter l'espace pour une meilleure visibilité

        // Pour chaque cours
        coursePlanning.forEach((course, index) => {
            // Capturer le cours avec html2canvas
            html2canvas(course, { 
                scale: 1,
                useCORS: true,
                logging: false
            }).then(canvas => {
                // Ajouter une nouvelle page si nécessaire (sauf pour le premier cours)
                if (index > 0) {
                    doc.addPage();
                    yPosition = 20;
                }
                
                const imgData = canvas.toDataURL('image/png');
                const imgWidth = pageWidth - 40; // marges
                const imgHeight = (canvas.height * imgWidth) / canvas.width;
                
                // Vérifier si l'image tient sur la page
                if (yPosition + imgHeight > pageHeight) {
                    doc.addPage();
                    yPosition = 20;
                }
                
                doc.addImage(imgData, 'PNG', 20, yPosition, imgWidth, imgHeight);
                
                // Si c'est le dernier cours, sauvegarder le PDF
                if (index === coursePlanning.length - 1) {
                    doc.save('planification-annuelle.pdf');
                }
            });
        });
    });

    // Ajouter un premier cours par défaut
    addNewCourse();

    // Créer une image de logo par défaut
    function createDefaultLogo() {
        const canvas = document.createElement('canvas');
        canvas.width = 200;
        canvas.height = 80;
        const ctx = canvas.getContext('2d');
        
        // Fond
        ctx.fillStyle = '#3498db';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Texte
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('LOGO ÉCOLE', canvas.width / 2, canvas.height / 2);
        
        return canvas.toDataURL('image/png');
    }

    // Définir le logo par défaut si aucun n'est défini
    if (!schoolLogo.src || schoolLogo.src === window.location.href) {
        const defaultLogo = createDefaultLogo();
        schoolLogo.src = defaultLogo;
    }
});
