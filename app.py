# Start the Flask app and create an Ngrok tunnel
public_url = ngrok.connect(5000)
print("Ngrok URL:", public_url)

app = Flask(__name__, template_folder='flask_code/templates', static_folder='flask_code/static')


# ---------------------------------------------- Homepage Route --------------------------------------------

@app.route("/", methods=["GET", "POST"])
def homepage():
    if request.method == "POST":
      # Check if GPU is available
      print('Checking for GPU...')
      if not torch.cuda.is_available():
          sys.exit('No GPU in runtime. Please go to the "Runtime" menu, "Change runtime type" and select "GPU".')

      # Start timer
      start_time = time.time()

      # Check if SyncKing-Kong folder already exists
      if not os.path.exists('/content/SyncKing-Kong'):
          print("Cloning SyncKing-Kong repository...")
          giturl = 'https://github.com/Mashood-Basharat/SyncKing-Kong.git'
          !git clone {giturl}
          %cd 'SyncKing-Kong'
          !mkdir 'face_alignment' 'temp'
      else:
          print('SyncKing-Kong folder already exists.')
          %cd '/content/SyncKing-Kong'

      working_directory = os.getcwd()

      # Install prerequisites only if not already installed
      try:
          import batch_face
          print('batch_face is already installed.')
      except ImportError:
          print('Installing batch_face...')
          !pip install batch_face --quiet

      try:
          import basicsr
          if basicsr.__version__ == '1.4.2':
              print('basicsr 1.4.2 is already installed.')
          else:
              raise ImportError
      except ImportError:
          print('Installing basicsr 1.4.2...')
          !pip install basicsr==1.4.2 --quiet
          print('Fixing basicsr degradations.py...')
          !cp /content/SyncKing-Kong/degradations.py /usr/local/lib/python3.10/dist-packages/basicsr/data/degradations.py

      try:
          import gfpgan
          print('gfpgan is already installed.')
      except ImportError:
          print('Installing gfpgan...')
          !pip install gfpgan --quiet

      # Run additional installation script
      print("Running additional installation...")
      !python install.py

      clear_output()
      print("Installation complete, move to Step 2!")

      # End timer
      elapsed_time = time.time() - start_time
      from easy_functions import format_time
      print(f"Execution time: {format_time(elapsed_time)}")

      # After setup, render the homepage with a success message
      return render_template(
          "homepage.html",
          message="Setup complete! Environment has been successfully set up.",
      )

    # First look when user enter the app
    return render_template("homepage.html")


#------------------------------------------- upload route --------------------------------------------------

@app.route('/upload', methods=['GET', 'POST'])
def upload_media():
    # Directory to store uploaded files
    UPLOAD_FOLDER = 'uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Create the upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if request.method == 'POST':
        # Clear previous uploads
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Handle video upload
        video_file = request.files.get('video')
        video_path = None
        if video_file:
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename)
            video_file.save(video_path)

        # Handle audio upload
        audio_file = request.files.get('audio')
        audio_path = None
        if audio_file:
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
            audio_file.save(audio_path)

        # Redirect to lipsyncing route, passing video and audio paths
        return redirect(url_for('lipsyncing', video_file=video_path, audio_file=audio_path))

    return render_template('upload.html', show_header=False)


#--------------------------------------------- Lipsyncing route --------------------------------------------------------------


@app.route('/lipsyncing', methods=['GET', 'POST'])
def lipsyncing():
    # Get the uploaded file paths from the request (passed from /upload route)
    video_file = request.args.get('video_file')
    audio_file = request.args.get('audio_file')

    if request.method == 'POST':
        # Collect lip-syncing parameters from the form
        quality = request.form.get('quality')
        output_height = request.form.get('output_height')
        use_previous_tracking_data = request.form.get('use_previous_tracking_data', 'off') == 'on'
        wav2lip_version = request.form.get('wav2lip_version')
        nosmooth = request.form.get('nosmooth', 'off') == 'on'

        # Padding parameters
        U = int(request.form.get('U'))
        D = int(request.form.get('D'))
        L = int(request.form.get('L'))
        R = int(request.form.get('R'))

        # Masking options
        size = float(request.form.get('size'))
        feathering = int(request.form.get('feathering'))
        mouth_tracking = request.form.get('mouth_tracking', 'off') == 'on'
        debug_mask = request.form.get('debug_mask', 'off') == 'on'

        # Other parameters (optional features)
        batch_process = request.form.get('batch_process', 'off') == 'on'
        output_suffix = request.form.get('output_suffix', '_SyncKing-Kong')
        include_settings_in_suffix = request.form.get('include_settings_in_suffix', 'off') == 'on'
        preview_input = request.form.get('preview_input', 'off') == 'on'
        preview_settings = request.form.get('preview_settings', 'off') == 'on'
        frame_to_preview = int(request.form.get('frame_to_preview', 0))

        # Save the parameters into a configuration file
        import configparser
        config = configparser.ConfigParser()

        # Prepare dictionary for options
        options = {
            'video_file': video_file,
            'vocal_file': audio_file,
            'quality': quality,
            'output_height': output_height,
            'wav2lip_version': wav2lip_version,
            'use_previous_tracking_data': use_previous_tracking_data,
            'nosmooth': nosmooth
        }
        padding = {
            'U': U,
            'D': D,
            'L': L,
            'R': R
        }
        mask = {
            'size': size,
            'feathering': feathering,
            'mouth_tracking': mouth_tracking,
            'debug_mask': debug_mask
        }
        other = {
            'batch_process': batch_process,
            'output_suffix': output_suffix,
            'include_settings_in_suffix': include_settings_in_suffix,
            'preview_input': preview_input,
            'preview_settings': preview_settings,
            'frame_to_preview': frame_to_preview
        }

        # Add these dictionaries to the config file
        config['OPTIONS'] = options
        config['PADDING'] = padding
        config['MASK'] = mask
        config['OTHER'] = other

        # Write the configuration to an INI file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        # Run the lip-syncing process using Colab-oriented execution
        try:
            print("Starting lip-syncing...")
            # Execute the run.py script using Colab-compatible syntax
            get_ipython().system('python run.py')

            # Check if the result video is generated
            output_video_path = os.path.join('/content/SyncKing-Kong/temp', 'output.mp4')

            if os.path.isfile(output_video_path):
                # Move the generated video to a static folder (so it can be served)
                static_video_path = os.path.join('/content/flask_code/static', 'output.mp4')
                os.rename(output_video_path, static_video_path)

            # Redirect to the /result route to display the video
            return redirect(url_for('result', video_path=static_video_path))

        except Exception as e:
            return render_template('lipsyncing.html', error=f"Error during lip-syncing: {str(e)}", show_header=False)

    # Display the lipsyncing page for initial GET request with prefilled video and audio files
    return render_template('lipsyncing.html', video_file=video_file, audio_file=audio_file, show_header=False)



#---------------------------------------------- result route --------------------------------------------------------------

@app.route('/result')
def result():
    video_path = request.args.get('video_path')
    if video_path and os.path.isfile(video_path):
        # Extract just the filename for Flask's `url_for` method
        video_filename = os.path.basename(video_path)
        return render_template('result.html', video_filename=video_filename, show_header=False)
    return "No video found", 404


#---------------------------------------------- feedback route ---------------------------------------------------------------------

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


#---------------------------------------------- submit feedback route --------------------------------------------------------------

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    rating = request.form.get('rating')
    comments = request.form.get('comments')
    # You can add code here to process/store feedback data
    return redirect(url_for('feedback'))  # Redirect back to feedback or another thank-you page

#-----------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app.run()
