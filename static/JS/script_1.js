const canvas1 = document.getElementById("canvas1");
const ctx1 = canvas1.getContext("2d");
const clear1 = document.getElementById("clear1");
const eq1 = document.getElementById("eq1");
const soln = document.getElementById("soln");
const error = document.getElementById("error");
const calc = document.getElementById("calc");
const upload1 = document.getElementById("upload1");
const lineWidth = 2;
const lineColor = "#000";

function prepareCanvas(canvas, ctx, clearBtn) {
    const canvasWidth = canvas.clientWidth;
    const canvasHeight = canvas.clientHeight;
    let isDrawing = false;
    let curPos;

    canvas.width = canvasWidth;
    canvas.height = canvasHeight;

    function getPosition(clientX, clientY) {
        let box = canvas.getBoundingClientRect();
        return { x: clientX - box.x, y: clientY - box.y };
    }

    function draw(e) {
        if (isDrawing) {
            let pos = getPosition(e.clientX, e.clientY);

            ctx.strokeStyle = lineColor;
            ctx.lineWidth = lineWidth;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            ctx.beginPath();
            ctx.moveTo(curPos.x, curPos.y);
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            ctx.closePath();
            curPos = pos;
        }
    }

    canvas.onmousedown = function (e) {
        isDrawing = true;
        curPos = getPosition(e.clientX, e.clientY);
        draw(e);
    };

    canvas.onmousemove = function (e) {
        draw(e);
    };

    canvas.onmouseup = function (e) {
        isDrawing = false;
    };

    clearBtn.addEventListener("click", clearCanvas);

    function clearCanvas() {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    }
    clearCanvas();

    upload1.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = new Image();
                img.onload = function () {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    const scale = Math.min(canvas.width / img.width, canvas.height / img.height);
                    const x = (canvas.width - img.width * scale) / 2;
                    const y = (canvas.height - img.height * scale) / 2;
                    ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
}

prepareCanvas(canvas1, ctx1, clear1);

calc.addEventListener("click", () => {
    const imgData1 = canvas1.toDataURL().split(",")[1];

    let data = {
        Image1: imgData1,
    };

    clearAnswer();

    fetch("/upload1", {
        method: "POST",
        headers: {
            Accept: "application/json, text/plain, */*",
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
        .then((res) => res.json())
        .then((res) => {
            if (res.Success) {
                eq1.innerText = res.Eqn_1;
                soln.innerText = res.Soln_X; // Correctly display the solution for X
            } else {
                error.innerText = res.Error;
            }
        });
});

function clearAnswer() {
    eq1.innerText = "";
    soln.innerText = "";
    error.innerText = "";
}