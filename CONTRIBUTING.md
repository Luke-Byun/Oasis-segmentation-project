# Contributing

Thank you for helping improve this research repository.

## Before opening a change

- Keep participant data, model weights, predictions, and credentials out of Git.
- Preserve notebook outputs unless clearing them is part of the proposed change.
- Explain any dataset, label-map, preprocessing, or metric assumptions.
- Do not present research outputs as clinical diagnoses.

## Development workflow

1. Fork the repository and create a focused branch.
2. Create a virtual environment and install the requirements for the component
   you are changing.
3. Make the smallest coherent change and update the relevant documentation.
4. Run Python syntax checks and verify edited notebooks still contain valid JSON.
5. Open a pull request describing the motivation, validation, and limitations.

## Commit style

Use short, descriptive commit messages, for example:

```text
docs: clarify nnU-Net artifact requirements
fix: resolve runtime path handling in Gradio app
```

## Reporting problems

Include the operating system, Python version, command, relevant configuration,
and complete error message. Never attach medical data or secrets to an issue.
