# coding=utf-8
# Copyright 2022 The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Generation configuration class and utilities."""

import os
from typing import Union
from ..utils import PushToHubMixin, logging

logger = logging.get_logger(__name__)


class GenerationConfig(PushToHubMixin):
    r"""
    Class that holds a configuration for a generation task.

    <Tip>

    A configuration file can be loaded and saved to disk. Loading the configuration file and using this file to
    initialize a model does **not** change its configuration or weights. It only affects the model's behavior at
    generation time.

    </Tip>

    Arg:
        max_length (`int`, *optional*, defaults to `20`):
            The maximum length the generated tokens can have. Corresponds to the length of the input prompt +
            `max_new_tokens`. In general, prefer the use of `max_new_tokens`, which ignores the number of tokens in
            the prompt.
        max_new_tokens (`int`, *optional*):
            The maximum numbers of tokens to generate, ignoring the number of tokens in the prompt.
        min_length (`int`, *optional*, defaults to `0`):
            The minimum length of the sequence to be generated.
        early_stopping (`bool`, *optional*, defaults to `False`):
            Whether to stop the beam search when at least `num_beams` sentences are finished per batch or not.
        max_time(`float`, *optional*):
            The maximum amount of time you allow the computation to run for in seconds. generation will still
            finish the current pass after allocated time has been passed.

        do_sample (`bool`, *optional*, defaults to `False`):
            Whether or not to use sampling ; use greedy decoding otherwise.
        num_beams (`int`, *optional*, defaults to `1`):
            Number of beams for beam search. 1 means no beam search.
        num_beam_groups (`int`, *optional*, defaults to `1`):
            Number of groups to divide `num_beams` into in order to ensure diversity among different groups of
            beams. [this paper](https://arxiv.org/pdf/1610.02424.pdf) for more details.
        penalty_alpha (`float`, *optional*):
            The values balance the model confidence and the degeneration penalty in contrastive search decoding.

        temperature (`float`, *optional*, defaults to `1.0`):
            The value used to module the next token probabilities.
        top_k (`int`, *optional*, defaults to `50`):
            The number of highest probability vocabulary tokens to keep for top-k-filtering.
        top_p (`float`, *optional*, defaults to `1.0`):
            If set to float < 1, only the smallest set of most probable tokens with probabilities that add up to
            `top_p` or higher are kept for generation.
        typical_p (`float`, *optional*, defaults to `1.0`):
            The amount of probability mass from the original distribution to be considered in typical decoding. If
            set to 1.0 it takes no effect. See [this paper](https://arxiv.org/pdf/2202.00666.pdf) for more details.
        diversity_penalty (`float`, *optional*, defaults to `0.0`):
            This value is subtracted from a beam's score if it generates a token same as any beam from other group
            at a particular time. Note that `diversity_penalty` is only effective if `group beam search` is
            enabled.
        repetition_penalty (`float`, *optional*, defaults to `1.0`):
            The parameter for repetition penalty. 1.0 means no penalty. See [this
            paper](https://arxiv.org/pdf/1909.05858.pdf) for more details.
        length_penalty (`float`, *optional*, defaults to `1.0`):
            Exponential penalty to the length that is used with beam-based generation. It is applied as an exponent
            to the sequence length, which in turn is used to divide the score of the sequence. Since the score is
            the log likelihood of the sequence (i.e. negative), `length_penalty` > 0.0 promotes longer sequences,
            while `length_penalty` < 0.0 encourages shorter sequences.
        no_repeat_ngram_size (`int`, *optional*, defaults to `0`):
            If set to int > 0, all ngrams of that size can only occur once.
        bad_words_ids(`List[List[int]]`, *optional*):
            List of token ids that are not allowed to be generated. In order to get the token ids of the words that
            should not appear in the generated text, use `tokenizer(bad_words, add_prefix_space=True,
            add_special_tokens=False).input_ids`.
        force_words_ids(`List[List[int]]` or `List[List[List[int]]]`, *optional*):
            List of token ids that must be generated. If given a `List[List[int]]`, this is treated as a simple
            list of words that must be included, the opposite to `bad_words_ids`. If given `List[List[List[int]]]`,
            this triggers a [disjunctive constraint](https://github.com/huggingface/transformers/issues/14081),
            where one can allow different forms of each word.
        use_cache (`bool`, *optional*, defaults to `True`):
            Whether or not the model should use the past last key/values attentions (if applicable to the model) to
            speed up decoding.
        renormalize_logits (`bool`, *optional*, defaults to `False`):
            Whether to renormalize the logits after applying all the logits processors or warpers (including the
            custom ones). It's highly recommended to set this flag to `True` as the search algorithms suppose the
            score logits are normalized but some logit processors or warpers break the normalization.
        forced_bos_token_id (`int`, *optional*, defaults to `model.config.forced_bos_token_id`):
            The id of the token to force as the first generated token after the `decoder_start_token_id`. Useful
            for multilingual models like [mBART](../model_doc/mbart) where the first generated token needs to be
            the target language token.
        forced_eos_token_id (`int`, *optional*, defaults to `model.config.forced_eos_token_id`):
            The id of the token to force as the last generated token when `max_length` is reached.
        remove_invalid_values (`bool`, *optional*, defaults to `model.config.remove_invalid_values`):
            Whether to remove possible *nan* and *inf* outputs of the model to prevent the generation method to
            crash. Note that using `remove_invalid_values` can slow down generation.
        exponential_decay_length_penalty (`tuple(int, float)`, *optional*):
            This Tuple adds an exponentially increasing length penalty, after a certain amount of tokens have been
            generated. The tuple shall consist of: `(start_index, decay_factor)` where `start_index` indicates
            where penalty starts and `decay_factor` represents the factor of exponential decay
        suppress_tokens  (`List[int]`, *optional*):
            A list of tokens that will be supressed at generation. The `SupressTokens` logit processor will set
            their log probs to `-inf` so that they are not sampled.
        begin_suppress_tokens  (`List[int]`, *optional*):
            A list of tokens that will be supressed at the begining of the generation. The `SupressBeginTokens`
            logit processor will set their log probs to `-inf` so that they are not sampled.
        forced_decoder_ids (`List[List[int]]`, *optional*):
            A list of pairs of integers which indicates a mapping from generation indices to token indices that
            will be forced before sampling. For example, `[[1, 123]]` means the second generated token will always
            be a token of index 123.

        num_return_sequences(`int`, *optional*, defaults to `1`):
            The number of independently computed returned sequences for each element in the batch.
        output_attentions (`bool`, *optional*, defaults to `False`):
            Whether or not to return the attentions tensors of all attention layers. See `attentions` under
            returned tensors for more details.
        output_hidden_states (`bool`, *optional*, defaults to `False`):
            Whether or not to return the hidden states of all layers. See `hidden_states` under returned tensors
            for more details.
        output_scores (`bool`, *optional*, defaults to `False`):
            Whether or not to return the prediction scores. See `scores` under returned tensors for more details.
        return_dict_in_generate (`bool`, *optional*, defaults to `False`):
            Whether or not to return a [`~utils.ModelOutput`] instead of a plain tuple.

        pad_token_id (`int`, *optional*):
            The id of the *padding* token.
        bos_token_id (`int`, *optional*):
            The id of the *beginning-of-sequence* token.
        eos_token_id (`int`, *optional*):
            The id of the *end-of-sequence* token.

        encoder_no_repeat_ngram_size (`int`, *optional*, defaults to `0`):
            If set to int > 0, all ngrams of that size that occur in the `encoder_input_ids` cannot occur in the
            `decoder_input_ids`.
        decoder_start_token_id (`int`, *optional*):
            If an encoder-decoder model starts decoding with a different token than *bos*, the id of that token.

        generation_kwargs:
            Additional generation kwargs will be forwarded to the `generate` function of the model. Kwargs that are not
            present in `generate`'s signature will be used in the model forward pass.
    """

    def __init__(self, **kwargs):
        # Parameters that control the length of the output
        self.max_length = kwargs.pop("max_length", 20)
        self.max_new_tokens = kwargs.pop("max_new_tokens", None)
        self.min_length = kwargs.pop("min_length", 0)
        self.early_stopping = kwargs.pop("early_stopping", False)
        self.max_time = kwargs.pop("max_time", None)

        # Parameters that control the generation strategy used
        self.do_sample = kwargs.pop("do_sample", False)
        self.num_beams = kwargs.pop("num_beams", 1)
        self.num_beam_groups = kwargs.pop("num_beam_groups", 1)
        self.penalty_alpha = kwargs.pop("penalty_alpha", None)

        # Parameters for manipulation of the model output logits
        self.temperature = kwargs.pop("temperature", 1.0)
        self.top_k = kwargs.pop("top_k", 50)
        self.top_p = kwargs.pop("top_p", 1.0)
        self.typical_p = kwargs.pop("typical_p", 1.0)
        self.diversity_penalty = kwargs.pop("diversity_penalty", 0.0)
        self.repetition_penalty = kwargs.pop("repetition_penalty", 1.0)
        self.length_penalty = kwargs.pop("length_penalty", 1.0)
        self.no_repeat_ngram_size = kwargs.pop("no_repeat_ngram_size", 0)
        self.bad_words_ids = kwargs.pop("bad_words_ids", None)
        self.force_word_ids = kwargs.pop("force_word_ids", None)
        self.forced_bos_token_id = kwargs.pop("forced_bos_token_id", None)
        self.forced_eos_token_id = kwargs.pop("forced_eos_token_id", None)
        self.remove_invalid_values = kwargs.pop("remove_invalid_values", False)
        self.exponential_decay_length_penalty = kwargs.pop("exponential_decay_length_penalty", None)
        self.suppress_tokens = kwargs.pop("suppress_tokens", None)
        self.begin_suppress_tokens = kwargs.pop("begin_suppress_tokens", None)
        self.forced_decoder_ids = kwargs.pop("forced_decoder_ids", None)

        # Parameters that define the output of `generate`
        self.num_return_sequences = kwargs.pop("num_return_sequences", 1)
        self.output_attentions = kwargs.pop("output_attentions", False)
        self.output_hidden_states = kwargs.pop("output_hidden_states", False)
        self.output_scores = kwargs.pop("output_scores", False)
        self.return_dict_in_generate = kwargs.pop("return_dict_in_generate", False)

        # Special tokens
        self.pad_token_id = kwargs.pop("pad_token_id", None)
        self.bos_token_id = kwargs.pop("bos_token_id", None)
        self.eos_token_id = kwargs.pop("eos_token_id", None)

        # Encoder-decoder generation parameters
        self.encoder_no_repeat_ngram_size = kwargs.pop("encoder_no_repeat_ngram_size", 0)
        self.decoder_start_token_id = kwargs.pop("decoder_start_token_id", None)

        # Wild card
        self.generation_kwargs = kwargs.pop("generation_kwargs", {})

    def save_pretrained(self, save_directory: Union[str, os.PathLike], push_to_hub: bool = False, **kwargs):
        """
        Save a configuration object to the directory `save_directory`, so that it can be re-loaded using the
        [`~PretrainedConfig.from_pretrained`] class method.

        Args:
            save_directory (`str` or `os.PathLike`):
                Directory where the configuration JSON file will be saved (will be created if it does not exist).
            push_to_hub (`bool`, *optional*, defaults to `False`):
                Whether or not to push your model to the Hugging Face model hub after saving it. You can specify the
                repository you want to push to with `repo_id` (will default to the name of `save_directory` in your
                namespace).
            kwargs:
                Additional key word arguments passed along to the [`~utils.PushToHubMixin.push_to_hub`] method.
        """
        if os.path.isfile(save_directory):
            raise AssertionError(f"Provided path ({save_directory}) should be a directory, not a file")

        os.makedirs(save_directory, exist_ok=True)

        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id, token = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)

        # If we have a custom config, we copy the file defining it in the folder and set the attributes so it can be
        # loaded from the Hub.
        if self._auto_class is not None:
            custom_object_save(self, save_directory, config=self)

        # If we save using the predefined names, we can load using `from_pretrained`
        output_config_file = os.path.join(save_directory, CONFIG_NAME)

        self.to_json_file(output_config_file, use_diff=True)
        logger.info(f"Configuration saved in {output_config_file}")

        if push_to_hub:
            self._upload_modified_files(
                save_directory, repo_id, files_timestamps, commit_message=commit_message, token=token
            )
