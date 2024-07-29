import asyncio
import logging
import schedule

from flask import Flask, request, jsonify

from main import app, random_night_message, send_message, random_time

flask_app = Flask(__name__)
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("flask_bot.log"),
                              logging.StreamHandler()])

# TODO: написать как использовать api

@flask_app.route('/postpone_message', methods=['POST'])
def postpone_message():
    try:
        data = request.json
        new_time = data.get('time')
        if not new_time:
            return jsonify({"error": "Time not provided"}), 400
        
        schedule.clear('night')
        schedule.every().day.at(new_time).do(lambda: asyncio.create_task(send_message(random_night_message()))).tag('night')
        return jsonify({"message": f"Message postponed to: {new_time}"}), 200
    except Exception as e:
        logging.error(f"Error in postpone_message: {e}")
        return jsonify({"error": str(e)}), 500


@flask_app.route('/cancel_message', methods=['POST'])
def cancel_message():
    try:
        schedule.clear('night')
        return jsonify({"message": "Message sending canceled."}), 200
    except Exception as e:
        logging.error(f"Error in cancel_message: {e}")
        return jsonify({"error": str(e)}), 500


@flask_app.route('/change_message', methods=['POST'])
def change_message():
    try:
        data = request.json
        new_message = data.get('message')
        if not new_message:
            return jsonify({"error": "Message not provided"}), 400
        
        schedule.clear('night')
        schedule.every().day.at(random_time("23:44", "01:24")).do(lambda: asyncio.create_task(send_message(new_message))).tag('night')
        return jsonify({"message": f"Message changed to: {new_message}"}), 200
    except Exception as e:
        logging.error(f"Error in change_message: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=3030)
