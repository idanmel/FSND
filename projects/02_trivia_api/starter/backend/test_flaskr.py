import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql:///{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data['categories']), 0)

    def test_get_peginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertGreater(data['total_questions'], 0)
        self.assertGreater(len(data['categories']), 0)
        self.assertLess(len(data['questions']), QUESTIONS_PER_PAGE + 1)

    def test_page_number_too_big(self):
        """When requesting for a page number that has no question,
        return 404"""
        res = self.client().get('/questions?page=12')
        self.assertEqual(res.status_code, 404)

    def test_delete_question(self):
        res = self.client().delete('/questions/5')
        self.assertEqual(res.status_code, 204)
        pass

    def test_delete_wrong_id(self):
        res = self.client().delete('/questions/400')
        self.assertEqual(res.status_code, 422)

    def test_add_question(self):
        new_question = {
            "question": "What is your name?",
            "answer": "Idan",
            "difficulty": 5,
            "category": 1
        }
        res = self.client().post('/questions', json=new_question)
        self.assertEqual(res.status_code, 201)

    def test_search(self):
        """Get a question back when you search for 'mirrors'"""
        search_term = {
            "searchTerm": "mirrors"
        }
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertGreater(len(data["questions"]), 0)

    def test_questions_by_category(self):
        res = self.client().get('categories/1/questions')
        self.assertEqual(res.status_code, 200)

        # make sure all the questions are in category 1
        data = res.json
        for question in data["questions"]:
            self.assertEqual(question["category"], 1)

    def test_questions_by_category_with_wrong_category(self):
        res = self.client().get('categories/130/questions')
        self.assertEqual(res.status_code, 404)

    def test_quizzes(self):
        data = {
            "previous_questions": [16],
            "quiz_category": {"id": 2},
        }
        res = self.client().post('quizzes', json=data)
        data = res.json

        self.assertEqual(res.status_code, 200)
        self.assertNotEqual(data["question"]["id"], 16)

    def test_quizzes_without_data(self):
        res = self.client().post('quizzes')
        self.assertEqual(res.status_code, 422)

    def test_address_not_found(self):
        res = self.client().delete('/questionssss')
        self.assertEqual(res.status_code, 404)

    def test_method_not_allowed(self):
        res = self.client().post('/categories')
        self.assertEqual(res.status_code, 405)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
