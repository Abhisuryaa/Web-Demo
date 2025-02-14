// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Quiz functionality
class Quiz {
    constructor() {
        this.currentQuestion = 0;
        this.score = 0;
        this.questions = [];
    }

    async loadQuestions() {
        try {
            const response = await fetch('/api/questions');
            this.questions = await response.json();
            this.displayQuestion();
        } catch (error) {
            console.error('Error loading questions:', error);
        }
    }

    displayQuestion() {
        const questionContainer = document.getElementById('quiz-container');
        if (!questionContainer) return;

        const question = this.questions[this.currentQuestion];
        questionContainer.innerHTML = `
            <div class="quiz-question">
                <h4 class="mb-3">${question.text}</h4>
                <div class="options">
                    ${question.options.map((option, index) => `
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="answer" 
                                   id="option${index}" value="${index}">
                            <label class="form-check-label" for="option${index}">
                                ${option}
                            </label>
                        </div>
                    `).join('')}
                </div>
                <button class="btn btn-primary mt-3" onclick="quiz.submitAnswer()">
                    ${this.currentQuestion === this.questions.length - 1 ? 'Finish' : 'Next'}
                </button>
            </div>
        `;
    }

    submitAnswer() {
        const selectedOption = document.querySelector('input[name="answer"]:checked');
        if (!selectedOption) return;

        const answer = parseInt(selectedOption.value);
        if (answer === this.questions[this.currentQuestion].correct) {
            this.score++;
        }

        this.currentQuestion++;
        
        if (this.currentQuestion < this.questions.length) {
            this.displayQuestion();
        } else {
            this.finishQuiz();
        }
    }

    async finishQuiz() {
        try {
            const response = await fetch('/submit_quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ score: this.score })
            });
            
            if (response.ok) {
                const quizContainer = document.getElementById('quiz-container');
                quizContainer.innerHTML = `
                    <div class="text-center">
                        <h3>Quiz Completed!</h3>
                        <p class="lead">Your score: ${this.score}/${this.questions.length}</p>
                        <a href="/dashboard" class="btn btn-primary">Return to Dashboard</a>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error submitting quiz:', error);
        }
    }
}

// Initialize quiz if on quiz page
if (document.getElementById('quiz-container')) {
    const quiz = new Quiz();
    quiz.loadQuestions();
}

// Profile image preview
const profileImageInput = document.getElementById('profile-image');
if (profileImageInput) {
    profileImageInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('profile-preview').src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
}

// Dynamic form fields
const addFieldButton = document.getElementById('add-field');
if (addFieldButton) {
    addFieldButton.addEventListener('click', function() {
        const container = document.getElementById('dynamic-fields');
        const fieldCount = container.children.length;
        
        const newField = document.createElement('div');
        newField.className = 'input-group mb-3';
        newField.innerHTML = `
            <input type="text" class="form-control" name="field${fieldCount}" required>
            <button class="btn btn-outline-danger" type="button" onclick="this.parentElement.remove()">
                Remove
            </button>
        `;
        
        container.appendChild(newField);
    });
}
