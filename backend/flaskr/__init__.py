import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    paginated_questions = questions[start:end]
    return paginated_questions


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
      return response
    
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/api/categories", methods=["GET"])
    def get_all_categories():
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}
        categories_length = len(formatted_categories)

        if len(formatted_categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": formatted_categories,
                "total_categories": categories_length,
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

     TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/api/questions", methods=["GET"])
    def get_paginated_questions():
        questions = Question.query.order_by(Question.id).all()
        paginated_questions = paginate_questions(request, questions)
        total_questions = len(questions)
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}

        if len(paginated_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": paginated_questions,
                "categories": formatted_categories,
                "total_questions": total_questions,
                "current_category": "Art",
            }
        )


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id>',methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404, "Item not found")

        try:
            db.session.delete(question)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
        finally:
            db.session.close()

        return jsonify({"success": True, "id": question_id}), 204

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """


    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty,
            )
            question.insert()
        
            return jsonify({
                "status": True, 
                "question": question.id}), 201
        
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/api/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get("searchTerm", None)
        questions = Question.query.filter(
            Question.question.ilike(f"%{search_term}%")
        ).all()

        if questions:
            resultQuestions = paginate_questions(request, questions)
            return (
                jsonify(
                    {
                        "success": True,
                        "questions": resultQuestions,
                        "total_questions": len(questions),
                    }
                ),
                200,
            )
        else:
            abort(404, "no result found")


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/api/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        category = Category.query.get(category_id)

        if category is None:
            abort(404, "Category does not exist")

        questions_in_category = Question.query.filter(
            Question.category == str(category_id)
        ).all()
        paginated_questions = paginate_questions(request, questions_in_category)

        if len(paginated_questions) == 0:
            abort(404)

        return (
            jsonify(
                {
                    "success": True,
                    "questions": paginated_questions,
                    "total_questions": len(questions_in_category),
                    "current_category": category.type,
                }
            ),
            200,
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/api/quizzes", methods=["POST"])
    def get_quizzes():
        try:

            body = request.get_json()
            previous_questions = body.get("previous_questions", None)
            quiz_category = body.get("quiz_category", None)
            category_id = quiz_category["id"]

            if category_id == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)
                ).all()

            else:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions),
                    Question.category == str(category_id),
                ).all()

                question = random.choice(questions)

            return (
                jsonify(
                    {
                        "success": True,
                        "question": question.format(),
                    }
                ),
                200,
            )
        except Exception as e:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Not found"
          }), 404

    @app.errorhandler(422)
    def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
          }), 422

    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
          }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "method not allowed"
          }), 405
    
    

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
    return app

