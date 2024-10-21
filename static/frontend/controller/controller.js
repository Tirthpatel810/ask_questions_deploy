app.controller('controller', function($scope, $http) {
    $scope.question = '';
    $scope.answers = [];
    $scope.show_data_reddit = false;
    $scope.show_data_stackoverflow = false;
    $scope.msg = '';
    $scope.recipient_email = '';
    $scope.status_email = '';
    $scope.status_translate = '';
    $scope.translated_data = '';
    $scope.sender = '';

    $scope.languages = [
        "afrikaans", "albanian", "amharic", "arabic", "armenian", "azerbaijani",
        "basque", "belarusian", "bengali", "bosnian", "bulgarian", "catalan",
        "cebuano", "chinese (simplified)", "chinese (traditional)", "corsican",
        "croatian", "czech", "danish", "dutch", "english", "esperanto", "estonian",
        "filipino", "finnish", "french", "frisian", "galician", "georgian",
        "german", "greek", "gujarati", "haitian creole", "hausa", "hawaiian",
        "hebrew", "hindi", "hmong", "hungarian", "icelandic", "igbo", "indonesian",
        "irish", "italian", "japanese", "javanese", "kannada", "kazakh", "khmer",
        "korean", "kurdish (kurmanji)", "kyrgyz", "lao", "latin", "latvian", "lithuanian",
        "luxembourgish", "macedonian", "malagasy", "malay", "malayalam", "maltese",
        "maori", "marathi", "mongolian", "myanmar (burmese)", "nepali", "norwegian",
        "odia", "pashto", "persian", "polish", "portuguese", "punjabi", "romanian",
        "russian", "samoan", "scots gaelic", "serbian", "sesotho", "shona", "sindhi",
        "sinhala", "slovak", "slovenian", "somali", "spanish", "sundanese", "swahili",
        "swedish", "tajik", "tamil", "telugu", "thai", "turkish", "ukrainian", "urdu",
        "uyghur", "uzbek", "vietnamese", "welsh", "xhosa", "yiddish", "yoruba", "zulu"
    ];


    $scope.translateQuestion = function(question_text,sender) {
        $scope.status_translate = 'Question is been translated wait a moment...';
        const requestData = {
            question: question_text,
            language: $scope.selectedLanguage
        };

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        $http({
            method: 'POST',
            url: '/translate-question/',
            data: requestData,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(function(response) {
            $scope.status_translate = '';
            $scope.sender = sender;
            $scope.translated_data = response.data.translated_question;
        }, function(error) {
            console.log("Error in translation:", error);
        });
    };

    // Get Answer from Reddit
    $scope.get_answer_from_reddit = function() {
        $scope.show_data_stackoverflow = false;
        $scope.msg = 'Wait for a moment, data is being collected from Reddit...';
        $http.post('http://127.0.0.1:8000/api/get_reddit_answers/', { question: $scope.question })
            .then(function(response) {
                if (response.data.answers && response.data.answers.length > 0) {
                    $scope.answers = response.data.answers.map(function(answer) {
                        return {
                            title: answer.title,
                            description: answer.description || 'Description not available',
                            url: answer.url
                        };
                    });
                    $scope.show_data_reddit = true;
                    $scope.msg = '';
                } else {
                    $scope.msg = 'No data available for your question on Reddit.';
                }
            })
            .catch(function(error) {
                if (error.status === 404) {
                    $scope.msg = 'Data not available for your question on Reddit.';
                } else {
                    $scope.msg = 'An error occurred while fetching data from Reddit.';
                }
            });
    };

    // Get Answer from StackOverflow
    $scope.get_answer_from_stackoverflow = function() {
        $scope.show_data_reddit = false;
        $scope.msg = 'Wait for a moment, data is being collected from StackOverflow...';
        $http.post('http://127.0.0.1:8000/api/get_stackoverflow_answers/', { question: $scope.question })
            .then(function(response) {
                if (response.data.answers && response.data.answers.length > 0) {
                    $scope.answers = response.data.answers.map(function(answer) {
                        return {
                            title: answer.title,
                            tags: answer.tags,
                            answer_count: answer.answer_count || 0,
                            url: answer.link
                        };
                    });
                    $scope.show_data_stackoverflow = true;
                    $scope.msg = '';
                } else {
                    $scope.msg = 'No data available for your question on StackOverflow.';
                }
            })
            .catch(function(error) {
                if (error.status === 404) {
                    $scope.msg = 'Data not available for your question on StackOverflow.';
                } else {
                    $scope.msg = 'An error occurred while fetching data from StackOverflow.';
                }
            });
    };

    $scope.toggleDescription = function(answer) {
        answer.expanded = !answer.expanded;
    };

    $scope.generateAndSendReport = function(get_recipient_email) {
        $scope.status_email = "wait a moment your report is prepared..."
        if (!get_recipient_email) {
            console.error('Invalid email address');
            alert("Please enter a email address.");
            return;
        } else {
            console.log(get_recipient_email);
        }

        const requestData = {
            answers: $scope.answers,
            email: get_recipient_email
        };

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        $http({
            method: 'POST',
            url: '/generate-report/',
            data: requestData,
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(function(response) {
            $scope.status_email = '';
            alert("Report sent successfully!");
            console.log("Success: ", response);
        }, function(error) {
            $scope.status_email = '';
            alert("Error occurred while sending the report.");
            console.error("Error: ", error);
        });
    };
    $scope.speak = function(text) {
        var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
        $http({
            method: 'POST',
            url: '/speak/',
            data: {text: text},
            headers: {
                'X-CSRFToken': csrftoken
            }
        }).then(function(response) {
            if (response.data.status === 'success') {
                console.log('Speech started');
            } else {
                console.error('Error in speech:', response.data.message);
            }
        }).catch(function(error) {
            console.error('Error in API call:', error);
        });
    };
});