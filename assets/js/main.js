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

    restext: "",
    anslist: [],

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

    partextHighlight(restext, bg) {
      var restext_ = escapeRegExp(restext);
      var partext_ = this.partext;

      if ( restext_ ) {
        var re = new RegExp(`(${restext_})`, "giu");
        var partext_ = partext_.replace(re, `<span class=\"highlight ${bg}\">$1</span>`);
      }

      return partext_ + '\n.';
    },

    selectQuestion(qtext, alist, id) {
      this.qustext = qtext;
      this.anslist = alist;
      this.submitQuestionCore(id);
    },

    submitQuestion() {
      this.anslist = [];
      this.submitQuestionCore(null);
    },

    submitQuestionCore(id) {
      this.loading = true;
      this.restext = "";

      const data = {
        paragraph: this.partext,
        question:  this.qustext,
        id:        id
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
      this.restext = "";
      this.anslist = [];
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
