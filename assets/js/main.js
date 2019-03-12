"use strict"

var app = new Vue({
  delimiters:["${", "}"],
  el: "#main",

  data: {
    pardata: _data.pardata,
    qadata:  _data.qadata,

    qalist: [],

    topic: "",
    partext: "",
    qustext: "",

    anstext: "",
    restext: "",

    loading: false
  },

  watch: {
    topic: function ( val ) {
      this.partext = this.pardata[val] || "";
      this.qalist  = this.qadata[val]  || "";
      this.clearQuestion();
    }
  },

  methods: {

    partextHighlight() {
      var anstext = escapeRegExp(this.anstext);
      var restext = escapeRegExp(this.restext);
      var partext_ = this.partext;

      if ( anstext && anstext == restext ) {
        var re = new RegExp(`(\\b|\\s|^)(${anstext})(\\b|\\s|$)`, "giu");
        var partext_ = partext_.replace(re, "$1<span class=\"highlight bg-primary\">$2</span>$3");
      } else {
        if ( anstext ) {
          var re = new RegExp(`(\\b|\\s|^)(${anstext})(\\b|\\s|$)`, "giu");
          var partext_ = partext_.replace(re, "$1<span class=\"highlight bg-success\">$2</span>$3");
        }

        if ( restext ) {
          var re = new RegExp(`(\\b|\\s|^)(${restext})(\\b|\\s|$)`, "giu");
          var partext_ = partext_.replace(re, "$1<span class=\"highlight bg-warning\">$2</span>$3");
        }
      }

      return partext_ + '\n.';
    },

    selectQuestion(qtext, atext) {
      this.qustext = qtext;
      this.anstext = atext;
      this.submitQuestionCore();
    },

    submitQuestion() {
      this.anstext = "";
      this.submitQuestionCore();
    },

    submitQuestionCore() {
      this.loading = true;
      this.restext = "";

      const data = {
        paragraph: this.partext,
        question:  this.qustext
      };

      this.$http.post("/post", data, {
        timeout: 60000
      }).then(
        res => {
          this.loading = false;
          this.restext = res.body.result;
        },
        res => {
          this.loading = false;
          customStatusError(res);
        }
      );
    },

    clearQuestion() {
      this.qustext = "";
      this.clearAnswer();
    },

    clearAnswer() {
      this.anstext = "";
      this.restext = "";
    }

  }

});

function escapeRegExp(str) {
  return str.replace(/[|\\{}()[\]^$+*?.]/g, "\\$&");
}

function customStatusError(res) {
  if ( res.status === 0 ) {
    res.statusText = 'Timeout'
  }
  var message = res.body ? res.body.message : "Unknown error";
  console.error(message, `[${res.status}] ${res.statusText}`);
  swal({
    title: `[${res.status}] ${res.statusText}`,
    text:  message,
    type:  "error"
  });
}
