console.log('whiteboard.js is loaded');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM is fully loaded');
    const canvas = document.getElementById('whiteboard');
    console.log('Canvas element:', canvas);
    if (canvas) {
        const ctx = canvas.getContext('2d');
        console.log('Canvas context:', ctx);

        // Set canvas size to window size
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        console.log('Canvas size set to:', canvas.width, 'x', canvas.height);

        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;
        let currentEquation = '';
        let equations = [];
        let cursorVisible = true;
        let cursorInterval;

        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('click', setTextPosition);
        window.addEventListener('keydown', handleKeyPress);

        function startDrawing(e) {
            isDrawing = true;
            [lastX, lastY] = [e.clientX, e.clientY];
        }

        function draw(e) {
            if (!isDrawing) return;
            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(e.clientX, e.clientY);
            ctx.stroke();
            [lastX, lastY] = [e.clientX, e.clientY];
        }

        function stopDrawing() {
            isDrawing = false;
        }

        function setTextPosition(e) {
            [lastX, lastY] = [e.clientX, e.clientY];
            redraw();
            startBlinkingCursor();
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') {
                if (currentEquation.includes('=')) {
                    solveEquation();
                } else {
                    currentEquation += '\n';
                    lastY += 20; // Move to next line
                }
            } else if (e.key === 'Backspace') {
                currentEquation = currentEquation.slice(0, -1);
            } else if (e.key.length === 1) {
                currentEquation += e.key;
            }
            redraw();
            resetCursorBlink();
        }

        function redraw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.font = '16px Arial';
            ctx.fillStyle = 'black';

            // Draw all previous equations
            equations.forEach(eq => {
                ctx.fillText(eq.input, eq.x, eq.y);
                if (eq.result) {
                    ctx.fillText(eq.result, eq.x + ctx.measureText(eq.input).width, eq.y);
                }
            });

            // Draw current equation
            ctx.fillText(currentEquation, lastX, lastY);

            // Draw cursor
            if (cursorVisible) {
                const cursorX = lastX + ctx.measureText(currentEquation).width;
                ctx.beginPath();
                ctx.moveTo(cursorX, lastY - 15);
                ctx.lineTo(cursorX, lastY + 2);
                ctx.stroke();
            }
        }

        function startBlinkingCursor() {
            if (cursorInterval) clearInterval(cursorInterval);
            cursorInterval = setInterval(() => {
                cursorVisible = !cursorVisible;
                redraw();
            }, 500);
        }

        function resetCursorBlink() {
            cursorVisible = true;
            if (cursorInterval) clearInterval(cursorInterval);
            startBlinkingCursor();
        }

        function solveEquation() {
            const equationToSolve = currentEquation.trim();
            console.log('Sending equation to solve:', equationToSolve);
            fetch('/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ equation: equationToSolve }),
            })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw err; });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Received response:', data);
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    equations.push({ input: equationToSolve, x: lastX, y: lastY, result: ` ${data.result}` });
                    currentEquation = '';
                    lastY += 20; // Move to next line
                    redraw();
                })
                .catch(error => {
                    console.error('Error solving equation:', error);
                    let errorMessage = error.message || 'Unknown error occurred';
                    equations.push({ input: equationToSolve, x: lastX, y: lastY, result: ` Error: ${errorMessage}` });
                    currentEquation = '';
                    lastY += 20; // Move to next line
                    redraw();
                });
        }

        // Draw initial red square
        ctx.fillStyle = 'red';
        ctx.fillRect(10, 10, 100, 100);
        console.log('Test rectangle drawn');

        startBlinkingCursor();
    } else {
        console.error('Canvas element not found');
    }
});