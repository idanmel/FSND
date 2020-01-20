import os
import random

from flask import Flask, abort, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from models import Category, Question, setup_db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after
    completing the TODOs
    '''
    CORS(app, resources={r"/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')

        return response

    @app.route('/categories')
    def categories():
        '''
        @TODO:
        Create an endpoint to handle GET requests
        for all available categories.
        '''
        categories = Category.query.all()
        all_categories = {c.id: c.type for c in categories}
        return jsonify({
            "categories": all_categories
        })

    @app.route('/questions', methods=['GET'])
    def questions():
        '''
        @TODO:
        Create an endpoint to handle GET requests for questions,
        including pagination (every 10 questions).
        This endpoint should return a list of questions,
        number of total questions, current category, categories.

        TEST: At this point, when you start the application
        you should see questions and categories generated,
        ten questions per page and pagination at the
        bottom of the screen for three pages.
        Clicking on the page numbers should update the questions.
        '''
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = Question.query.all()
        current_questions = [q.format() for q in questions[start:end]]
        if not current_questions:
            abort(404)

        categories = Category.query.all()
        all_categories = {c.id: c.type for c in categories}
        return jsonify({
            "questions": current_questions,
            "total_questions": len(questions),
            "categories": all_categories,
            "current_category": None,
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''
        @TODO:
        Create an endpoint to DELETE question using a question ID.

        TEST: When you click the trash icon next to a question,
        the question will be removed.
        This removal will persist in the database and when you refresh the page.
        '''
        q = Question.query.filter_by(id=question_id).first()
        try:
            q.delete()
        except:
            abort(422)
        else:
            return jsonify({}), 204

    @app.route('/questions', methods=['POST'])
    def add_question():
        '''
        @TODO:
        Create an endpoint to POST a new question,
        which will require the question and answer text,
        category, and difficulty score.

        TEST: When you submit a question on the "Add" tab,
        the form will clear and the question will appear at the end of the last
        page of the questions list in the "List" tab.
        '''
        data = request.json
        q = Question(
            question=data['question'],
            answer=data['answer'],
            difficulty=data['difficulty'],
            category=data['category'],
        )
        q.insert()
        return jsonify({}), 201

    @app.route('/questions/search', methods=['POST'])
    def search():
        '''
        @TODO:
        Create a POST endpoint to get questions based on a search term.
        It should return any questions for whom the search term
        is a substring of the question.

        TEST: Search by any phrase. The questions list will update to include
        only question that include that string within their question.
        Try using the word "title" to start.
        '''
        questions = Question.query.all()
        search_term = request.json["searchTerm"]
        current_questions = [
            question.format() for question in questions
            if search_term.lower() in question.question.lower()
        ]

        return jsonify({
            "questions": current_questions,
            "total_questions": len(questions),
            "current_category": None,
        })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_by_category(category_id):
        '''
        @TODO:
        Create a GET endpoint to get questions based on category.

        TEST: In the "List" tab / main screen, clicking on one of the
        categories in the left column will cause only questions of that
        category to be shown.
        '''
        category = Category.query.get_or_404(category_id)
        questions = Question.query.all()
        current_questions = [
            question.format() for question in questions
            if question.category == category.id
        ]

        return jsonify({
            "questions": current_questions,
            "total_questions": len(current_questions),
            "current_category": category_id,
        }), 200

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        '''
        @TODO:
        Create a POST endpoint to get questions to play the `quiz`.
        This endpoint should take category and previous question parameters
        and return a random questions within the given category,
        if provided, and that is not one of the previous questions.

        TEST: In the "Play" tab, after a user selects "All" or a category,
        one question at a time is displayed, the user is allowed to answer
        and shown whether they were correct or not.
        '''
        try:
            previous_questions = request.json["previous_questions"]
            category_id = int(request.json["quiz_category"]["id"])
            questions = Question.query.all()
            if category_id == 0:
                category_questions = questions
            else:
                category_questions = [
                    q for q in questions if q.category == int(category_id)
                ]

            new_questions = [
                q for q in category_questions if q.id not in previous_questions
            ]

            random_question = random.choice(new_questions)
        except:
            abort(422)

        return jsonify({
            "question": random_question.format(),
        }), 200

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    def error_handler(status, error):
        return jsonify({
            "success": False,
            "error": status,
            "message": str(error)
        }), status

    @app.errorhandler(400)
    def not_found(error):
        return error_handler(400, error)

    @app.errorhandler(404)
    def not_found(error):
        return error_handler(404, error)

    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_handler(405, error)

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return error_handler(422, error)

    @app.errorhandler(500)
    def server_error(error):
        return error_handler(500, error)

    return app
