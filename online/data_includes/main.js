PennController.ResetPrefix(null);
DebugOff();


// HELPER FUNCTIONS
function createTextSequence(primeText, targetText, timings) {
    return [
        newText("mask", "+").color('white').css("font-size", '0.6em').css("font-family", "Courier New, monospace").print("center at 50vw", "middle at 50vh"),
        newTimer("maskTimer", timings.mask).start().wait(),
        getText("mask").remove(),
        
        newText("mask2", " "),
        newTimer("mask2Timer", timings.mask2).start().wait(),
        getText("mask2").remove(),

        newText("prime", primeText).log().color('white').css("font-size", '0.6em').css("font-family", "Courier New, monospace").print("center at 50vw", "middle at 50vh"),
        newTimer("primeTimer", timings.prime).start().wait(),
        getText("prime").remove(),
        
        newText("mask3", " "),
        newTimer("mask3Timer", timings.mask3).start().wait(),
        getText("mask3").remove(),

        newText("target", targetText).log().color('white').css("font-size", '0.6em').css("font-family", "Courier New, monospace").print("center at 50vw", "middle at 50vh"),
        newTimer("targetTimer", timings.target).start().wait(),
        getText("target").remove(),
        
        newText("mask4", " ")
    ];
}

function createJitter(jitterTime) {
    return [
        newText("jitter", " "),
        newTimer("jitterTimer", jitterTime).start().wait(),
        getText("jitter").remove()
    ];
}

// CONFIGURATION
const CONFIG = {
    experiment: {
        totalBlocks: 8,
        trialsPerBlock: 25,
        duration: "10 minutes"
    },
    
    timings: {
        mask: 200,
        mask2: 200, 
        prime: 300,
        mask3: 500,
        target: 300,
        feedback: 500
    },
    
    jitter: {
        min: 300,
        max: 700,
        step: 10
    },
    
    keys: {
        same: "2",
        different: "1",
        continue: " "
    }
};

// GLOBAL VARIABLES
let correctCount = 0;
let jitterValues = [];

// UTILITY FUNCTIONS
function initializeJitter() {
    for (let i = CONFIG.jitter.min; i <= CONFIG.jitter.max; i += CONFIG.jitter.step) {
        jitterValues.push(i);
    }
}

function sample(array) {
    let sel = Math.floor(Math.random() * array.length / 10) * 10;
    return array[sel];
}

function SepWithN(sep, main, n) {
    this.args = [sep, main];
    this.run = function(arrays) {
        assert(arrays.length == 2, "Wrong number of arguments (or bad argument) to SepWithN");
        assert(parseInt(n) > 0, "N must be a positive number");
        let sep = arrays[0];
        let main = arrays[1];

        if (main.length <= 1) return main;
        
        let newArray = [];
        while (main.length) {
            for (let i = 0; i < n && main.length > 0; i++)
                newArray.push(main.shift());
            for (let j = 0; j < sep.length; ++j)
                newArray.push(sep[j]);
        }
        return newArray;
    };
}

function sepWithN(sep, main, n) { return new SepWithN(sep, main, n); }

// INITIALIZATION
initializeJitter();

// EXPERIMENT SEQUENCE
Sequence(
    "consent", 
    "prolificid", 
    "welcome", 
    "instructions",
    randomize("practice"),
    "begin", 
    sepWithN("break", randomize("test"), CONFIG.experiment.trialsPerBlock),
    "send", 
    "final"
);

// STYLING
Header(
    newHtml("<style> \
        body { \
            width: 100%; \
            margin: 0; \
            padding: 50px; \
            background-color: gray; \
            font-family: Arial, sans-serif; \
        } \
        p { \
            color: white; \
            font-family: Arial, sans-serif; \
            font-style: normal; \
            font-weight: normal; \
            text-decoration: none; \
            font-size: 0.6em; \
            margin: 10pt 0; \
            text-align: left; \
        } \
        .s1 { \
            color: white; \
            font-family: Arial, sans-serif; \
            font-style: normal; \
            font-weight: bold; \
            text-decoration: none; \
            font-size: 11pt; \
        } \
        button { \
            font-size: 11px; \
            padding: 3px 12px; \
            border-radius: 4px; \
            font-family: Arial, sans-serif; \
        } \
    </style>").print()
).log("ID", GetURLParameter("id"));

// TRIALS
newTrial("consent",
    newHtml("consent_form", "consent.html").print(),
    newButton("I consent to take part in this study").center().print().wait()
);

newTrial("prolificid",
    newHtml("prolific_screen", "prolific.html").center().print(),
    newTextInput("inputprolificid").center().print(),
    newButton("Confirm").center().css({'margin-bottom': '20px'}).print().wait(),
    newVar("prolificid").global().set(getTextInput("inputprolificid"))
).log("prolificid", getVar("prolificid"));

newTrial("welcome",
    newHtml("welcome_screen", "welcome.html").print(),
    newKey(CONFIG.keys.continue).wait()
);


newTrial("instructions",
    newHtml("instructions", "instructions.html").print(),
    newKey(CONFIG.keys.continue).wait()
);

Template("practice.csv", row => {
    let jitter = sample(jitterValues);
    let correctResponse = row.Sentence === row.Probe ? CONFIG.keys.same : CONFIG.keys.different;

    return newTrial("practice",
        newText("PRACTICE").color("white").css({"font-size": "20pt", "font-weight": "bold", "text-align": "center", "margin-bottom": "30px"}).print("center at 50vw", "top at 50px"),
        createTextSequence(row.Sentence, row.Probe, CONFIG.timings),
        
        newKey("answerTarget", "12").log().wait()
            .test.pressed(correctResponse)
            .success(
                newText("correct", "Correct").color("white").css("font-size", "20px")
                    .print("center at 50vw", "center at 50vh"),
                newFunction(() => correctCount += 1),
                newTimer("feedback-corr", CONFIG.timings.feedback)
            )
            .failure(
                newText("incorrect", "Wrong").color("white").css("font-size", "20px")
                    .print("center at 50vw", "center at 50vh"),
                newTimer("feedback-wrong", CONFIG.timings.feedback)
            ),
        
        createJitter(jitter)
    )
    .log("Match", row.Match)
    .log("Sentence", row.Sentence)
    .log("Probe", row.Probe)
    .log("Condition", row.Condition)
    .log("Jitter", jitter)
});


newTrial("begin",
    newHtml("begin_screen", "begin.html").print(),
    newKey(CONFIG.keys.continue).wait()
);


newTrial("break",
    newVar("block_n").global().set(v => (v||0) + 1),
    newVar("text").set(getVar("block_n")).set(v => "You have now completed block " + v + " of " + CONFIG.experiment.totalBlocks + "."),
    newText("prompt", "").text(getVar("text")).css("font-size", "15px").print(),
    newText("<p>When you are ready, press SPACE to continue.</p>").center().print(),
    newKey(CONFIG.keys.continue).wait()
);

Template("stimuli.csv", row => {
    let jitter = sample(jitterValues);
    let correctResponse = row.Sentence === row.Probe ? CONFIG.keys.same : CONFIG.keys.different;

    return newTrial("text_test",
        createTextSequence(row.Sentence, row.Probe, CONFIG.timings),
        newKey("answerTarget", "12").log().wait(),
        createJitter(jitter)
    )
    .log("Match", row.Match)
    .log("Sentence", row.Sentence)
    .log("Probe", row.Probe)
    .log("Condition", row.Condition)
    .log("Jitter", jitter)
});

SendResults("send");

newTrial("final",
    newHtml("final_screen", "final.html").print(),
    newText("<p><a href='https://app.prolific.com/submissions/complete?cc=foo' target='_blank'>Please click this link (completion code = 'foo') to confirm your participation and return to Prolific.</a></p>")
        .print(),
    // stay on this page forever    
    newButton().wait()
);