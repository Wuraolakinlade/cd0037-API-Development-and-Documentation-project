import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
      return response
    
    """
    # @TODO:
    # Create an endpoint to handle GET requests
    # for all available categories.
    # """
    @app.route("/categories", methods=["GET"])
    def get_categories():
        selection = Category.query.order_by(Category.id).all()
        current_categories = paginate_questions(request, selection)

        if len(current_categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": current_categories,
                "total_categories": len(Category.query.all()),
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

    @app.route("/questions", methods=["GET"])
    def get_questions():
        current_questions = paginate_questions(request, selection)
        total_questions = len(Question.query.order_by(Question.id).all())
        selection = Question.query.order_by(Question.id).all()

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": total_questions,
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
        try:
            question = Question.query.get(question_id)
            question.delete()
            selection = Question.query.order_by(question_id).all()
            current_questions = paginate_questions (request, selection)

            return jsonify({
                "success": True,
                "id": question_id,
                'questions': current_questions,
                "total_questions": len(Question.query.all()),
            })

        except:
            abort(422)

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
        search = body.get('search', None)



        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
                current_questions = paginate_questions (request, selection)

                return jsonify({
                    "success": True, 
                    "questions": current_questions,
                    'total_questions': len(selection.all())})

            else:
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty = new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
                })

        except:            
            abort(405)

    """
    # @TODO:
    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.

    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.
    # """

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        current_category = []
        try:
            search = '%{}%'.format(search_term)
            selection = Question.query.order_by(Question.category).filter(Question.question.ilike(search)).all()
            questions = paginate_questions(request, selection)

            categories = Question.query.with_entities(Question.category).order_by(Question.category).filter(Question.question.ilike(search)).all()
            for category in categories:
                for result in category:
                    current_category.append(result)

            return jsonify({
                'success': True,
                'questions': questions,
                'current_category': current_category,
                'total_questions': len(selection)
                })
        except:
            abort(404)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        category = Category.query.get(category_id)

        
        try: 
            selection = Question.query.order_by(Question.id).filter(Question.category == id).all() 
            current_questions = paginate_questions(request, selection)
      
            return jsonify({
          'success': True,
          'questions': current_questions,
          'current_category': Category.type,
          'total_questions': len(selection)
            })  
        except:
            abort(405)

    

    """
    # @TODO:
    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.

    # TEST: In the "Play" tab, after a user selects "All" or a category,
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.
    # """
    @app.route("/quizzes", methods=["POST"])
    def play_quizzes():
            selection = None
            body = request.get_json()
            quiz_category = body.get("quiz_category")
            past_ids = body.get("past_question")
            category_id = quiz_category.get('id')


            try:
                if category_id ==0:
                    # To retrieve all questions
                    selection = Question.query.all()

                else:
                    # To retrieve questions in the particular category
                    selection = Question.query.order_by(Question.id).filter(Question.category==category_id).all()
                    current_questions = paginate_questions(request, selection)  
                    if len(current_questions) == 0:
                        return jsonify({
                            "success": True,
                            "question": None
                        })

                    else:
                        question = random.choice(selection)
                        return (
                            jsonify(
                                {
                                    "success": True,
                                    "question": question.format(),
                                }
                            )
                        )
            except:
                abort(400)

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
          "message": "Resource not found"
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

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal server error"
            }), 500

    @app.errorhandler(503)
    def server_unavailable(error):
      return jsonify({
          "success": False,
          "error": 503,
          "message": "Server Unavailable"
          }), 503


    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
    return app

