const input1 = document.getElementById('num1');
const input2 = document.getElementById('num2');
const resultDisplay = document.getElementById('result');

const btnSum = document.getElementById('btn-sum');
const btnDiff = document.getElementById('btn-diff');
const btnMult = document.getElementById('btn-mult');
const btnDiv = document.getElementById('btn-div');

function sum(a, b) {
    return a + b;
}

function difference(a, b) {
    return a - b;
}

function product(a, b) {
    return a * b;
}

function division(a, b) {
    if (b === 0) {
        return null;
    }
    return a / b;
}

function getNumbers() {
    const val1 = input1.value.trim();
    const val2 = input2.value.trim();

    if (val1 === '' || val2 === '' || isNaN(val1) || isNaN(val2)) {
        return { error: 'Ошибка: введите числа!' };
    }

    return {
        a: parseFloat(val1),
        b: parseFloat(val2)
    };
}

function displayResult(value) {
    if (value === null) {
        resultDisplay.textContent = 'Ошибка: деление на ноль!';
        resultDisplay.classList.add('error');
    } else if (typeof value === 'string') {
        resultDisplay.textContent = value;
        resultDisplay.classList.add('error');
    } else {
        resultDisplay.textContent = value;
        resultDisplay.classList.remove('error');
    }
}

btnSum.addEventListener('click', () => {
    const data = getNumbers();
    if (data.error) {
        displayResult(data.error);
        return;
    }
    displayResult(sum(data.a, data.b));
});

btnDiff.addEventListener('click', () => {
    const data = getNumbers();
    if (data.error) {
        displayResult(data.error);
        return;
    }
    displayResult(difference(data.a, data.b));
});

btnMult.addEventListener('click', () => {
    const data = getNumbers();
    if (data.error) {
        displayResult(data.error);
        return;
    }
    displayResult(product(data.a, data.b));
});

btnDiv.addEventListener('click', () => {
    const data = getNumbers();
    if (data.error) {
        displayResult(data.error);
        return;
    }
    const res = division(data.a, data.b);
    if (res === null) {
        displayResult('Ошибка: деление на ноль!');
    } else {
        displayResult(res);
    }
});