# Example LLM Prompts for Telegram Analysis

After processing your Telegram chat data and splitting it into chunks, you'll want to provide effective instructions to your Large Language Model for analysis. Below are example prompts you can adapt for different analytical needs. 

## Essential for any llm instructions to anylise these chunks

*WARNING:* there's some info, without which, the llm has no chance of delivering anything remotely useful in relation to the chunks you're feeding it!

1. Data Format:
```
The data is in a pipe-separated format:
id|date_unixtime|from|from_id|text
(The first chunk might contain a header line # Format: ... which you can ignore for analysis).
```
2. What to expect and what it is to do about it:
```
After 'you' have acknowledged the instructions provided in this prompt, the next prompt you will receive from me will consist exclusively of the first data chunk.
```
	This could be followed either by instructions (per below examples) as to how to process the first chunk or with instructions on how to receive multiple-chunks before processing e.g.
```
This will be 1 of [N] chunks that I will add sequentially without further instruction. Do not respond to the first chunk other to acknowledge that 'you' have been able to discern the pipe-separated fields and that you are expecting as the next prompt chunk 2 of [N].

For subsequent chunks until the last, [N] of [N], respond only to acknowledge receipt and to confirm what 'you' are next expecting.

When you have received the final chunk, anylise all chunks as follows:
```

## General Conversation Summary

```
You are analyzing a portion of a Telegram group chat focused on [topic]. This is chunk [X] of [Y] from the period [date range].

Please provide:
1. A concise summary of the main topics discussed
2. Key points or insights shared
3. Questions raised but not answered
4. Notable contributors and their main perspectives

Present this information in a clear, structured format that highlights the most important elements of the discussion.
```

## Topic-Specific Analysis

```
You are analyzing a Telegram group chat about [broad topic]. I'm specifically interested in discussions related to [specific topic].

For this chunk of conversation from [date range]:
1. Extract and summarize all discussions related to [specific topic]
2. Note the different perspectives expressed
3. Highlight any consensus or disagreements
4. Identify any proposals, solutions, or action items mentioned
5. Note any resources shared (links, papers, tools) related to this topic

If [specific topic] is not discussed in this chunk, briefly summarize what is discussed instead and mention that the target topic is absent.
```

## Identifying Changes in Sentiment or Opinion

```
You are analyzing a portion of an ongoing conversation from a Telegram group focused on [topic]. This is chunk [X] of [Y].

Please identify:
1. How opinions on [specific issue] evolve in this portion of the conversation
2. Any significant shifts in group sentiment
3. Catalyst moments where viewpoints changed
4. Areas where consensus formed or dissolved

If you notice opinions that differ from those in a previous chunk (if I've mentioned those to you), highlight these changes and possible reasons for them.
```

## Technical Discussion Analysis

```
You are analyzing a technical discussion from a Telegram group focused on [technical domain]. This chunk covers [date range].

Please provide:
1. A summary of technical concepts discussed
2. Any problems or challenges identified
3. Solutions or approaches proposed
4. Technical trade-offs mentioned
5. Decisions made or consensus reached
6. Open questions or unresolved issues

Format technical terms, code snippets, or mathematical concepts clearly and explain complex ideas in accessible language.
```

## Chronological Development Tracking

```
You are analyzing a chunk of conversation from a Telegram group discussing [project/idea/proposal]. This is chunk [X] from [date range].

Please track the chronological development of [project/idea/proposal] by:
1. Noting how the conversation progressed over time
2. Identifying key decision points or milestones
3. Summarizing how ideas evolved or were refined
4. Highlighting when new participants joined the discussion and their impact
5. Creating a timeline of significant moments or insights

Present this information in a way that helps me understand the evolution of thinking around [project/idea/proposal].
```

## Comparative Analysis Between Chunks

```
You are helping me analyze a long Telegram conversation split into chunks. I've previously reviewed chunk [X] which covered [brief summary of previous chunk].

This is the next chunk from [date range]. Please:
1. Compare the content of this chunk with what I told you about the previous one
2. Highlight continuations of previous topics
3. Identify new topics or directions
4. Note any contradictions or changes in group thinking
5. Summarize how the conversation has evolved

Your analysis should help me understand the progression between chunks without having to manually connect the dots.
```

## Adapting These Prompts

When using these example prompts:
1. Replace bracketed text like [topic] with your specific subject matter
2. Add context from previous chunks when analyzing later portions
3. Specify any particular focus areas unique to your analysis needs
4. Consider providing some background on the group or conversation for better context

Remember that the effectiveness of LLM analysis depends on providing clear instructions and relevant context.
