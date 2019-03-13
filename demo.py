#!/usr/bin/env python3
# -*- coding:utf-8 -*-


__author__    = "Mu Yang <emfomy@gmail.com>"
__copyright__ = "Copyright 2019"

import json
import os
import random
import sys
import tempfile

import tensorflow as tf

import server

sys.path.insert(0, "bert")

from run_squad import convert_examples_to_features
from run_squad import FeatureWriter
from run_squad import flags
from run_squad import FLAGS
from run_squad import input_fn_builder
from run_squad import model_fn_builder
from run_squad import modeling
from run_squad import RawResult
from run_squad import read_squad_examples
from run_squad import SquadExample
from run_squad import tokenization
from run_squad import write_predictions

flags.DEFINE_string(
    "host", "0.0.0.0",
    "The host IP.")

flags.DEFINE_integer(
    "port", 9000,
    "The port.")

flags.DEFINE_string(
    "data", "data.json",
    "The SQuAD JSON file.")

FLAGS.__delattr__("do_train")
FLAGS.__delattr__("do_predict")
FLAGS.__delattr__("gcp_project")
FLAGS.__delattr__("num_train_epochs")
FLAGS.__delattr__("predict_file")
FLAGS.__delattr__("save_checkpoints_steps")
FLAGS.__delattr__("train_batch_size")
FLAGS.__delattr__("train_file")

class Demo():
    """The demo object"""

    def __init__(self, file):
        """Default constructor."""

        self.__pardata = {}
        self.__qadata  = {}
        with open(file) as fin:
            for data in json.load(fin)["data"]:
                title = data["title"]
                for i, item in enumerate(data["paragraphs"]):
                    key = f"{title}#{i+1:02}"
                    self.__pardata[key] = item["context"]
                    self.__qadata[key] = []
                    for subitem in item["qas"]:
                        anslist = [ans["text"] for ans in subitem["answers"]]
                        self.__qadata[key].append((subitem["question"], anslist, subitem["id"],))

        self.bert_core()


    def pardata(self):
        """Load paragraph data.

        Returns:
            dict: the paragraphs.
                * Key   (str): topic.
                * Value (str): paragraph.
        """

        return self.__pardata

    def qadata(self):
        """Load data.

        Returns:
            dict: the questions and answers.
                * Key   (str):  topic.
                * Value (list): list of (question, answer)s.
        """

        return self.__qadata

    def predict(self, p_str, q_str, idx=None):
        """Get predicted answer.

        Args:
            p_str (str): paragraph.
            q_str (str): questions.

        Returns:
            str: predicted answer.
        """
        if idx == None:
            idx = str(random.getrandbits(32))

        input_data = {
            "data": [
                {
                    "paragraphs": [
                        {
                            "context": p_str,
                            "qas": [
                                {"id": idx, "question": q_str}
                            ]
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w') as fout:
            json.dump(input_data, fout)
            fout.flush()
            results = self.bert_predict(fout.name)

        return results[idx]


    def bert_core(self):
        tf.logging.set_verbosity(tf.logging.INFO)

        bert_config = modeling.BertConfig.from_json_file(FLAGS.bert_config_file)

        validate_flags_or_throw(bert_config)

        tf.gfile.MakeDirs(FLAGS.output_dir)

        self.tokenizer = tokenization.FullTokenizer(
                vocab_file=FLAGS.vocab_file, do_lower_case=FLAGS.do_lower_case)

        tpu_cluster_resolver = None
        if FLAGS.use_tpu and FLAGS.tpu_name:
            tpu_cluster_resolver = tf.contrib.cluster_resolver.TPUClusterResolver(
                    FLAGS.tpu_name, zone=FLAGS.tpu_zone, project=FLAGS.gcp_project)

        is_per_host = tf.contrib.tpu.InputPipelineConfig.PER_HOST_V2
        run_config = tf.contrib.tpu.RunConfig(
                cluster=tpu_cluster_resolver,
                master=FLAGS.master,
                model_dir=FLAGS.output_dir,
                # save_checkpoints_steps=FLAGS.save_checkpoints_steps,
                tpu_config=tf.contrib.tpu.TPUConfig(
                        iterations_per_loop=FLAGS.iterations_per_loop,
                        num_shards=FLAGS.num_tpu_cores,
                        per_host_input_for_training=is_per_host))

        # train_examples = None
        num_train_steps = None
        num_warmup_steps = None

        model_fn = model_fn_builder(
                bert_config=bert_config,
                init_checkpoint=FLAGS.init_checkpoint,
                learning_rate=FLAGS.learning_rate,
                num_train_steps=num_train_steps,
                num_warmup_steps=num_warmup_steps,
                use_tpu=FLAGS.use_tpu,
                use_one_hot_embeddings=FLAGS.use_tpu)

        # If TPU is not available, this will fall back to normal Estimator on CPU
        # or GPU.
        self.estimator = tf.contrib.tpu.TPUEstimator(
                use_tpu=FLAGS.use_tpu,
                model_fn=model_fn,
                config=run_config,
                # train_batch_size=FLAGS.train_batch_size,
                predict_batch_size=FLAGS.predict_batch_size)


    def bert_predict(self, input_file):

        eval_examples = read_squad_examples(
            input_file=input_file, is_training=False)

        eval_writer = FeatureWriter(
                filename=os.path.join(FLAGS.output_dir, "eval.tf_record"),
                is_training=False)
        eval_features = []

        def append_feature(feature):
            eval_features.append(feature)
            eval_writer.process_feature(feature)

        convert_examples_to_features(
                examples=eval_examples,
                tokenizer=self.tokenizer,
                max_seq_length=FLAGS.max_seq_length,
                doc_stride=FLAGS.doc_stride,
                max_query_length=FLAGS.max_query_length,
                is_training=False,
                output_fn=append_feature)
        eval_writer.close()

        tf.logging.info("***** Running predictions *****")
        tf.logging.info("  Num orig examples = %d", len(eval_examples))
        tf.logging.info("  Num split examples = %d", len(eval_features))
        tf.logging.info("  Batch size = %d", FLAGS.predict_batch_size)

        all_results = []

        predict_input_fn = input_fn_builder(
                input_file=eval_writer.filename,
                seq_length=FLAGS.max_seq_length,
                is_training=False,
                drop_remainder=False)

        # If running eval on the TPU, you will need to specify the number of
        # steps.
        all_results = []
        for result in self.estimator.predict(
                predict_input_fn, yield_single_examples=True):
            if len(all_results) % 1000 == 0:
                tf.logging.info("Processing example: %d" % (len(all_results)))
            unique_id = int(result["unique_ids"])
            start_logits = [float(x) for x in result["start_logits"].flat]
            end_logits = [float(x) for x in result["end_logits"].flat]
            all_results.append(
                    RawResult(
                            unique_id=unique_id,
                            start_logits=start_logits,
                            end_logits=end_logits))

        with tempfile.NamedTemporaryFile(mode='r') as output_prediction_file_, \
             tempfile.NamedTemporaryFile(mode='r') as output_nbest_file_, \
             tempfile.NamedTemporaryFile(mode='r') as output_null_log_odds_file_:
            output_prediction_file    = output_prediction_file_.name
            output_nbest_file         = output_nbest_file_.name
            output_null_log_odds_file = output_null_log_odds_file_.name

            write_predictions(eval_examples, eval_features, all_results,
                              FLAGS.n_best_size, FLAGS.max_answer_length,
                              FLAGS.do_lower_case, output_prediction_file,
                              output_nbest_file, output_null_log_odds_file)

            results = json.load(output_prediction_file_)

        return results


def validate_flags_or_throw(bert_config):
    """Validate the input FLAGS or throw an exception."""
    tokenization.validate_case_matches_checkpoint(FLAGS.do_lower_case,
                                                  FLAGS.init_checkpoint)

    if FLAGS.max_seq_length > bert_config.max_position_embeddings:
        raise ValueError(
                "Cannot use sequence length %d because the BERT model "
                "was only trained up to sequence length %d" %
                (FLAGS.max_seq_length, bert_config.max_position_embeddings))

    if FLAGS.max_seq_length <= FLAGS.max_query_length + 3:
        raise ValueError(
                "The max_seq_length (%d) must be greater than max_query_length "
                "(%d) + 3" % (FLAGS.max_seq_length, FLAGS.max_query_length))


def main(_):
    """The main function."""

    demo = Demo(FLAGS.data)
    server.run(demo, FLAGS.host, FLAGS.port, debug=False)


if __name__ == "__main__":

    flags.mark_flag_as_required("vocab_file")
    flags.mark_flag_as_required("bert_config_file")
    tf.app.run()
    sys.exit()
