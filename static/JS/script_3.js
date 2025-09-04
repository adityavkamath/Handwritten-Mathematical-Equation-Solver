const canvas1 = document.getElementById("canvas1");
const canvas2 = document.getElementById("canvas2");
const canvas3 = document.getElementById("canvas3");

const ctx1 = canvas1.getContext("2d");
const ctx2 = canvas2.getContext("2d");
const ctx3 = canvas3.getContext("2d");

const clear1 = document.getElementById("clear1");
const clear2 = document.getElementById("clear2");
const clear3 = document.getElementById("clear3");

const upload1 = document.getElementById("upload1");
const upload2 = document.getElementById("upload2");
const upload3 = document.getElementById("upload3");

const eq1 = document.getElementById("eq1");
const eq2 = document.getElementById("eq2");
const eq3 = document.getElementById("eq3");

const X = document.getElementById("solnX");
const Y = document.getElementById("solnY");
const Z = document.getElementById("solnZ");

const error = document.getElementById("error");

const calc = document.getElementById("calc");

const lineWidth = 2;
const lineColor = "#000";

function prepareCanvas(canvas, ctx, clearBtn, uploadInput) {
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

    canvas.onmouseup = function () {
        isDrawing = false;
    };

    clearBtn.addEventListener("click", () => {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvasWidth, canvasHeight);
    });

    uploadInput.addEventListener("change", function () {
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

window.addEventListener("load", () => {
    prepareCanvas(canvas1, ctx1, clear1, upload1);
    prepareCanvas(canvas2, ctx2, clear2, upload2);
    prepareCanvas(canvas3, ctx3, clear3, upload3);
});

calc.addEventListener("click", () => {
    const img1 = canvas1.toDataURL().split(",")[1];
    const img2 = canvas2.toDataURL().split(",")[1];
    const img3 = canvas3.toDataURL().split(",")[1];

    let data = {
        Image1: img1,
        Image2: img2,
        Image3: img3,
    };

    clearAnswer();

    fetch("/upload3", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    })
        .then((res) => res.json())
        .then((res) => {
            if (res.Success) {
                eq1.innerText = res.Eqn_1;
                eq2.innerText = res.Eqn_2;
                eq3.innerText = res.Eqn_3;

                X.innerText = res.Soln_X;
                Y.innerText = res.Soln_Y;
                Z.innerText = res.Soln_Z;
            } else {
                error.innerText = res.Error;
            }
        });
});

function clearAnswer() {
    eq1.innerText = "";
    eq2.innerText = "";
    eq3.innerText = "";
    X.innerText = "";
    Y.innerText = "";
    Z.innerText = "";
    error.innerText = "";
}