"use strict"

var app = new Vue({
  delimiters:["${", "}"],
  el: "#main",

  data: {
    pardata: _data.pardata,
    ansdata: _data.ansdata,

    topic: "",
    partext: "",
    anslist: [],
    anstext: "",

    questext: "",
    questext2: "",

    loading: false
  },

  watch: {
    topic: function ( val ) {
      this.partext = this.pardata[val] || "";
      this.anslist = this.ansdata[val] || "";
      this.clearAnswer();
    }
  },

  methods: {

    partextHighlight() {
      var anstext = escapeRegExp(this.anstext);
      if ( anstext ) {
        var re = new RegExp(`(\\b|\\s|^)(${escapeRegExp(this.anstext)})(\\b|\\s|$)`, "giu");
        var partext_ = this.partext.replace(re, "$1<span class=\"highlight\">$2</span>$3");
      } else {
        var partext_ = this.partext;
      }
      return partext_ + '\n.';
    },

    selectAnswer(text) {
      this.anstext = text;
      this.submitAnswer();
    },

    submitAnswer() {
      this.loading = true;
      this.questext = "";
      this.questext2 = "";

      const data = {
        paragraph: this.partext,
        answer:    this.anstext
      };

      this.$http.post("/post", data, {
        timeout: 60000
      }).then(
        res => {
          this.loading = false;
          this.questext = res.body.question;
          this.questext2 = res.body.question2;
        },
        res => {
          this.loading = false;
          customStatusError(res);
        }
      );
    },

    clearAnswer() {
      this.anstext = "";
      this.questext = "";
      this.questext2 = "";
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
