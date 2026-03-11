# Generative Algorithmic Framework for Novel and Contextually Adaptive Percussion Synthesis

Student Details: student1, student2
Guided by: guide

## Agenda

* Abstract
* Problem Statement and Objectives
* Literature Review/ Background Study
* Design & Methodology
* Hardware and Software Requirements
* Implementation
* Results & Discussion
* Further Steps
* Conclusion
* References

## Abstract

* Rhythm is a foundational element in musical composition across all genres.
* This project introduces an AI-based system that generates creative, high-fidelity percussion beats with minimal input from musicians.
* The user simply specifies the time signature and musical genre, and the system auto-generates realistic drum patterns and sounds that helps the user to kick start their composition.
* Combines an Algorithmic Framework for rhythm generation and Generative Adversarial Networks (GANs) for percussive audio synthesis.
The goal is to assist musicians by offering instantly usable, expressive, and novel rhythmic backbones for composition and production.

## Problem Statement and Objectives

### Problem Statement

Musicians often require a rhythmic base to begin composing, but current tools either require technical skill or produce uninspired, repetitive patterns. There is a lack of integrated systems that generate both creative rhythmic patterns and expressive, high-quality percussion audio with minimal input.

### Objectives

* To build a user-friendly AI system that generates drum beats from just a time signature and genre input.
* To implement an Algorithmic framework for evolving rhythmic structures with musical features like syncopation and density.
* To use GANs to generate realistic, expressive audio for each percussion element.
* To offer novel and creative beats by incorporating creativity-promoting mechanisms in the learning process.
* To provide musicians with a fast, intuitive way to kickstart musical ideas or compositions.

## Literature Review/ Background Study

| S.No. | Author(s) | Paper Title | Key Points | Gaps |
|=======|===========|=============|============|======|
| 1.    | .....     | ....        | ....       | ...  |
| 2.    | .....     | ....        | ....       | ...  |

## Design & Methodology

* The problem is split into two parts: generation of a drum pattern, and fabrication of an audio waveform from the pattern.
* The goal is to generate drum patterns that are stylistically consistent with a given musical genre using a Conditional Generative Adversarial Network (cGAN).
* The cGAN architecture consists of two neural networks, a Generator that creates new drum patterns and a Discriminator that evaluates them.

## Hardware and Software Requirements

* point 1
* point 2
* point 3
* point 4
* point 5
* point 6

## Implementation

* The Groove MIDI Dataset (GMD) is used for training, providing a large collection of professionally recorded drum performances.
* Basic data analysis and exploration were performed to understand the dataset.
* The midi and style features are extracted from the dataset, where the genre, BPM, and time signature serves as the conditional input for the cGAN.
* The raw MIDI data is converted into a structured numerical format suitable for deep learning models.
* The data pipeline includes shuffling, batching, and prefetching to ensure efficient training and prevent bottlenecks.
    * The entire MIDI dataset cannot be loaded at once due to memory constraints.
    * It must be loaded one at a time.
    * Storing it is also not feasible.
    * Must be converted to IR and loaded while training.
* This results in training of the model to generate novel percussion patterns.

## Results & Discussion

* Early results show the Generator is able to produce rudimentary drum patterns that resemble real ones, but they may lack rhythmic complexity.
* The generated patterns can capture the general feel of the conditioned genre, such as the syncopation of a hip-hop beat or the straightforward rhythm of a rock song. A key challenge is preventing mode collapse, where the Generator produces only a limited variety of drum patterns, even with diverse conditioning.  
* Future work will focus on:
    * Improving the model's ability to generate longer, more intricate, and human-like drum fills and variations.
    * Generating audio waveforms from this IR.
* The subjective quality of the generated music can be evaluated by musicians and producers to validate the model's creative output beyond quantitative metrics.

## Further Steps

* Currently, the actual waveform generation is being done using a preset of sounds being played in the generated pattern.
* A further improvement is to generate the waveform using either:
    * an automatic dataset approach
    * GAN generation using a GAN-synth-like model
* Use a bigger model with the same architecture and more weights for a better result.

## Conclusion

* The implementation of a cGAN for drum generation shows promise as a tool for music production and algorithmic composition.
* The model learns to capture the complex rhythmic and stylistic nuances of real drum performances from the GMD.
* The conditional aspect is vital for controlling the output, allowing for genre-specific pattern generation.
* Addressing challenges like mode collapse is crucial for the practical application and creative versatility of the model.
* This project serves as a foundational step toward building more sophisticated AI-powered musical co-creators.

## References

`IEEE style references`

* point 1
* point 2
* point 3
* point 4
* point 5
* point 6

