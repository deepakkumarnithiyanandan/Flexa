import cv2
import mediapipe as mp
import numpy as np
import math
import time
import json
import os

# Ensure database folder exists
os.makedirs("./database", exist_ok=True)

# File path for workout history
WORKOUT_HISTORY_PATH = "./database/workout_history.json"

# Initialize MediaPipe Pose Estimation
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

# Define exercise landmark mappings and calorie burn per rep
WORKOUTS = {
    "Bicep Curls": (11, 13, 15),  # Shoulder, Elbow, Wrist
    "Squats": (24, 26, 28),       # Hip, Knee, Ankle
    "Push-ups": (12, 14, 16),     # Shoulder, Elbow, Wrist
    "Lunges": (24, 26, 28),       # Hip, Knee, Ankle
    "Deadlifts": (24, 26, 28),    # Hip, Knee, Ankle
    "Planks": (12, 14, 16),       # Shoulder, Elbow, Wrist
    "Bench Press": (12, 14, 16)   # Shoulder, Elbow, Wrist
}

CALORIES_PER_REP = {
    "Bicep Curls": 0.5,
    "Squats": 0.8,
    "Push-ups": 0.7,
    "Lunges": 0.6,
    "Deadlifts": 1.2,
    "Planks": 0.3,
    "Bench Press": 1.0
}

def findAngle(img, lmList, p1, p2, p3, draw=True):
    """Calculate the angle between three key points."""
    x1, y1 = lmList[p1][1:]
    x2, y2 = lmList[p2][1:]
    x3, y3 = lmList[p3][1:]
    
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    
    if draw:
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
        cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
        cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
        cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50), 
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    
    return angle

def track_exercise(exercise_name, rep_count):
    """Track exercise reps using webcam & MediaPipe pose estimation."""
    if exercise_name not in WORKOUTS:
        return {"success": False, "message": f"❌ Unsupported exercise: {exercise_name}"}
    
    cap = cv2.VideoCapture(0)  # Open webcam
    
    pTime = 0  # Track FPS
    dir = 0  # Movement direction (up/down)
    count = 0  # Rep count
    score_list = []  # Form score tracking
    
    # Timer setup
    exercise_duration = rep_count * 8  # Each rep is ~8 seconds
    start_time = time.time()
    end_time = start_time + exercise_duration

    while (time.time() - end_time) < 0:
        success, img = cap.read()
        if not success:
            break
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        lmList = []
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

            # Extract pose landmarks
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            # Exercise Tracking
            if len(lmList) != 0:
                p1, p2, p3 = WORKOUTS[exercise_name]
                angle = findAngle(img, lmList, p1, p2, p3)
                per = np.interp(angle, (60, 160), (100, 0))  # Normalize score
                score_list.append(per)

                if per == 100 and dir == 0:
                    count += 0.5  # Half rep completed
                    dir = 1
                if per == 0 and dir == 1:
                    count += 0.5  # Full rep completed
                    dir = 0

                # ✅ Only Display Rep Count (Removed "Reps" text)
                cv2.putText(img, str(int(count)), (500, 75), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

        # FPS Calculation
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        # Display Timer & FPS
        cv2.putText(img, f"FPS: {int(fps)}", (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        cv2.putText(img, f"Time Left: {int(end_time - time.time())}", (70, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        cv2.imshow("Workout Tracker", img)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
            break

    cap.release()
    cv2.destroyAllWindows()

    # Compute final score and calories burned
    average_score = sum(score_list) / len(score_list) if score_list else 0
    calories_burned = CALORIES_PER_REP.get(exercise_name, 0) * int(count)

    # Save workout history to JSON
    workout_data = {
        "exercise_name": exercise_name,
        "reps": int(count),
        "score": round(average_score, 2),
        "calories": round(calories_burned, 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    if os.path.exists(WORKOUT_HISTORY_PATH):
        with open(WORKOUT_HISTORY_PATH, "r") as file:
            history = json.load(file)
    else:
        history = []

    history.append(workout_data)

    with open(WORKOUT_HISTORY_PATH, "w") as file:
        json.dump(history, file, indent=4)

    return {
        "success": True,
        "message": f"✅ Workout Completed: {int(count)} reps | Calories Burned: {round(calories_burned, 2)} kcal",
        "reps": int(count),
        "calories": round(calories_burned, 2),
        "score": round(average_score, 2),
        "chart_path": "./database/form_score_chart.png"
    }
