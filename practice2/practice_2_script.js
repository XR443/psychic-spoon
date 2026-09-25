const resultEl = document.getElementById('result');
const plusBtn = document.getElementById('plusBtn');
const minusBtn = document.getElementById('minusBtn');
const messageEl = document.getElementById('message');

let count = 0;

function updateUI() {
    resultEl.textContent = count;

    if (count > 0) {
        resultEl.style.backgroundColor = 'yellow';
    } else if (count < 0) {
        resultEl.style.backgroundColor = 'green';
    } else {
        resultEl.style.backgroundColor = 'red';
    }

    plusBtn.disabled = (count >= 10);
    minusBtn.disabled = (count <= -10);

    if (count === 10 || count === -10) {
        messageEl.textContent = 'вы достигли экстремального значения';
    } else {
        messageEl.textContent = '';
    }
}

plusBtn.addEventListener('click', () => {
    if (count < 10) {
        count++;
        updateUI();
    }
});

minusBtn.addEventListener('click', () => {
    if (count > -10) {
        count--;
        updateUI();
    }
});

updateUI();