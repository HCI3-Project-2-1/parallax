# Project Manual - Bachelor Computer Science - Year 2

# Project 2.1 - Human-Computer Interaction

# Parallax View Real-time Human-Computer Interface

### Rico M ̈ockel

### 2024-

```
Period 1.1, 1.2, and 1.
Academic year 2024-
Department of Advanced Computing Sciences
Faculty of Science and Engineering
Maastricht University
```

Figure 1: Figure showing application using the parallax effect. Here, because there
is no movement and feedback, the effect is not visible but you merely see the
virtual 3D scene from one perspective. Image taken from (https://www.anxious-
bored.com/blog/2018/2/25/theparallaxview-illusion-of-depth-by-3d-head-tracking-on-
iphone-x) where you can see the actual effect.

## 1 Project Description

The central topic of this project is to develop and to evaluate a human-computer interface
that updates in real-time. For this you will be generating a visual scene that uses the
parallax effect (https://en.wikipedia.org/wiki/Parallax) to generate the illusion of a 3-
dimensional scene (for an example see Figure 1). The parallax effect describes what an
observer experiences when the observer moves parallel to a scene that contains objects at
different distances. Objects close to the observer seem to move faster than those far away
(see Figure 2). This effect can be used to generate the illusion of depth and 3-dimensional
objects on a 2-dimensional computer screen. To generate the 3-dimensional illusion you
will track the eye of a human observer and continuously update what the observer sees on
the computer screen.

### 1.1 Objectives

In this project you will explore how to build larger software projects by combining and
extending functionalities available through popular software libraries. The project lets
you practice the development of software that must run efficiently on decent computer
hardware as well as the generation of interactive computer graphics that must react in
real-time. You further practice the use of one of the most popular computer vision libraries:
OpenCV. You can explore popular computer graphics engines, and will apply your skills
in performing user studies to evaluate your self-developed human-computer interface.
In the first project phase you will design your software and select suitable software
components by exploring the available functionalities and real-time performance of popular
state-of-the-art software libraries. In the second project phase you will integrate different
functionalities into a single software project considering the real-time performance of your
software. In the third project phase you have the chance to finalise your software, expand
its functionalities, improve its performance, and to test it through a user study.


Figure 2: Figure showing parallax effect as experienced by passengers in a car. Objects
close to the car (in the foreground) appear to move quickly while far away objects (in the
background) seem to remain stationary. To the passenger this provides the perception of
3 dimensions.

### 1.2 Main Requirements

This section describes the main functional and non-functional requirements that your
project team and your product must fulfil:

- In the project you are required to apply the principles of good project management
    where all team members understand all parts of the software and contribute to its
    development. You are required to use Git, for version control, with your reposi-
    tory/repositories hosted on GitHub with public visibility.
- You are required to implement a graphical user interface that uses the parallax effect
    to generate the illusion of depth. To generate the 3-dimensional illusion you will track
    the eye of the human observer relative to the screen with the help of the webcam of
    your computer. For eye-tracking we recommend using the computer vision library
    OpenCV. You then update in real-time the display of the objects on the computer
    screen to generate the parallax effect. If implemented correctly, a human observer
    will get the illusion that the computer display is an actual window where some 3-
    dimensional objects are sticking out of the screen while others are deep inside. This
    effect only takes place if the update on the display happens sufficiently fast (= in
    real-time) to convince the human brain of the illusion. This is why you will have to
    take the performance of your developed code properly into account.
- In this project you are explicitly encouraged to make use of libraries for computer
    vision and computer graphics. The actual parallax effect must be implemented
    by yourself. See https://www.anxious-bored.com/blog/2018/2/25/theparallaxview-
    illusion-of-depth-by-3d-head-tracking-on-iphone-x for an example implementation for
    iOS.
- You must evaluate the performance of your software solution and its components.
    Performance here has several meanings that require different tests: (1) Does your
    software solution (and its components) provide the required functionalities? Under


```
which conditions does your software solution (or any of its components) no longer
function as requested? (E.g. eye tracking might only work under certain conditions.)
(2) Does your software solution (and its components) run in real-time without major
jitters and delays? (3) Does your software solution provide a convincing parallax
illusion?
```
- All of your experiments should be well-documented and easily reproducible. When-
    ever possible, parameters should be changed using configuration files, or, at the bare
    minimum, well-documented command-line arguments. If someone wanted to repro-
    duce your experiments (which they should be able to from the information provided
    in your GitHub page), it should not be necessary for them to manually change any
    lines of code in between experiments.
- A professional data analysis should be provided for performance evaluations and
    user studies. This requires that you pay attention to the distribution of statistical
    data (e.g. jitter/delays might not be normally distributed), derive mean values and
    standard deviations when applicable. To display data, provide meaningful plots. For
    the analysis of delays histograms might be useful. To show how much of a delay each
    software component contributes to the overall solution, pie charts might be a good
    choice. Do not overload reports and presentations with tables displaying raw data.
- You must evaluate the user experience you generate with your software by means
    of a proper user study. Implement and experiment with different versions of your
    software using multiple scenes of different complexity.
- You are explicitly allowed to choose from a number of programming languages in-
    cluding Java, Python, C++. Ask your examiners for permission in case you want
    to use additional programming languages. You are also free to choose a suitable
    graphics engine.
- In the project plagiarism will not be tolerated. Clearly state any material (including
    software components, ideas, graphics, text) that is not your original contribution
    and name the appropriate sources.

## 2 Project Tasks

The following three subsections describe in more detail what the minimum requirements
are for each phase, and how you will be assessed. The final assessment of the project as a
whole is a pass or a fail, based on whether or not the minimum requirements were satisfied,
but no more fine-grained grade. However, if you are able, we still strongly recommend
more deeply exploring any aspect of the project that you are interested in and exceeding
minimum requirements. While you cannot immediately be rewarded for this with a higher
grade, you will be able to gain valuable experience and to showcase your work in your
public GitHub profile, which many of your potential future employers will carefully look
at when making hiring decisions! In the end you are not performing the project for your
supervisors but to boost your skills and career opportunities.

### 2.1 First Project Phase

During the first project phase you will perform a detailed evaluation of available ap-
proaches to fulfil the described requirements. Based on criteria that you clearly define,
you will compare the identified approaches, argue why these approaches are suitable, and
decide which approaches you will use for your software development. You should identify
approaches at least for (1) eye tracking, (2) 3D scene visualisation as well as (3) for the


implementation of the parallax effect. We want you to put enough effort into researching
the approaches so that you can provide a detailed project plan for the second and third
project phase. To make informed decisions you will have to test software components and
evaluate their performance.
Assessment:At the end of the first project phase you will demonstrate your results to
your examiners in form of (1) a written project plan as well as (2) a short video (format:
mp4, length: 8 minutes max, size: 300MB max) in which you demonstrate your most
promising tested software components.
Your project plan should be written in a concise way and must at least include:

- An annotated block diagram and short description showing the envisioned software
    architecture. (Note: this is not a class diagram.) (1 page max)
- A comparison of the tested software components and considered approaches with a
    clear description of the performed tests and selected criteria. Based on the selected
    criteria, explain which software components and methods you select for the software
    implementation in the second and third project phases. (4 pages max)
- A description of the planned tasks for the second and third project phase. Tasks
    must be planned to lead to Specific, Measurable, Achievable, Realistic, and Timely
    goals. Provide a realistic planning where you assign clear responsibilities to all team
    members. (2 pages max)
- A Gantt chart displaying the timeline of your main tasks. (1 page max)
- A risk analysis table for your project. Identify at least 8 major risks, explain the
    impact of these risks on your project, and provide meaningful mitigation plans. (
    pages max)

### 2.2 Second Project Phase

Your focus during the second project phase will be on the implementation of a software
solution that integrates all required components. Furthermore you will evaluate and opti-
mise the performance of your solution and prepare to conduct a proper user study in the
third project phase.
Assessment:At the end of the second project phase you will provide a live demonstra-
tion of your solution to your examiners. This demonstration will take 20 minutes including
questions. Plan and test your demonstration before meeting the examiners. During the
demonstrations, provide the examiners with the opportunity to test your solutions so that
they may provide you with valuable feedback.
Peer feedback: Some time during the second half of project phase 2, two other
project groups provide you feedback on your solution. For this, a short live demonstration
is organised and you develop a short feedback form that project groups to fill out. You
are asked to consider this feedback to improve your software solution during the subse-
quent project phase. You can use this peer feedback demonstration also to improve your
preparations of the assessment.
Preparation of user study: Prepare your user study during the second project
phase in such a way that you can execute the user study early and smoothly during the
third project phase. Prepare your evaluation forms, perform some test runs, practice the
evaluation of the data, and schedule meetings with participants who are willing to test
your solution.
Hint:At the end of the third project phase you will have to submit a final report. Be
smart and make plans for this report already during the second project phase.


### 2.3 Third Project Phase

Improve the software you developed during the second project phase. Take the feedback
of your examiners and peer reviewers into account. Add more impressive scenes and other
features to explore at which point your computer system can no longer maintain real-time
performance. If your software lacked real-time performance so far, update it accordingly.
Carefully evaluate the performance of your software solution. All of your experiments
should be well-documented and easily reproducible. Last but not least, evaluate your
software through a professionally conducted user study.
Assessment: At the end of the third project phase you will provide a final written
report and will be assessed during a final product examination.
The final report (10 pages max including figures but excluding data tables that are
displayed in the appendix) should at the very least document (1) a short description of
your final solution, (2) a report on the conducted experiments, and (3) a description and
evaluation of the final user study. (4) A discussion section should provide insights into
lessons that you learned and a critical discussion of the final solution.
The product examination (taking about 30 minutes) will comprise a light presentation
on your final results combined with a live demonstration in which your examiner should
be able to perform live tests of your solution. Prepare a presentation that takes no more
than 5 minutes as well as the live demonstration. Reserve time for your examiners to ask
questions and to evaluate the code and software design of your solution. For the code
evaluation bring a laptop that can run the code.


