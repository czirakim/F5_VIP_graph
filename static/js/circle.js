const form = document.querySelector('form');
const submitButton = document.querySelector('#submitButton');
const progressBar = document.querySelector('#progressBar');

form.addEventListener('submit', (event) => {
  // prevent the default form submission behavior
  event.preventDefault();

  // show the progress bar
  progressBar.style.display = 'block';

  // start a timer to simulate a long-running operation
  let progress = 0;
  const timer = setInterval(() => {
    // update the progress bar
    progressBar.style.width = `${progress}%`;
    progress += 10;

    // if the progress reaches 100%, stop the timer and hide the progress bar
    if (progress > 100) {
      clearInterval(timer);
      progressBar.style.display = 'none';
      progressBar.style.width = '0%';
    }
  }, 500);
});
