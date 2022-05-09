Author = Stephen Luedtke
Version = 1.0
Description = The SPLBee App provides an interface in which to conduct SPL'ing Bees. The App includes a Real-time Scoring/Judging dashboard, Lookup Tables for questions and answers and directions on how to run the Bee.

Directions:

Please let me know if you have any questions or feedback at sluedtke@splunk.com. Enjoy!

For Moderators:

- Setup Notes: Install SPLBee App on an instance accessible over internet or local network where contestants will reside. The app includes the spl_bee index and a TCP input listening on 8999 for contestant submissions. You will also need to install Lookup Editor to edit questions/answers and keep score.

- I find it best to open each page on a separate tab: "SPLing Bee", "Edit Results", "Scoreboard", and "Edit Questions".
- The "SPLing Bee" Page will be used to deliver the questions and content.
- Add your questions and answers to the "Edit Questions" Page/Lookup. Please make sure you have tested your questions and answers for functionality and correctness before you begin the competition.
- At the end of each round/question, *** IMPORTANT *** copy the results table into the "Edit Results" Lookup. Append each round's results to the existing results. This will keep track of the scores from each round.
- Refresh Scoreboard to show overall results.

For Contestants:

- You will need a Splunk instance connected to the internet or local network where the master instance resides. This could be your own OR a Splunk Cloud Trial - https://www.splunk.com/page/sign_up/cloudtrial.
- You will need to download and install the Add-on for SPLing Bee App from Splunkbase and restart.
- Go to Settings --> Advanced Search --> Search Macros and edit the `sendresults` macro. Replace <yournamehere> with a unique name and <ip> with the IP Address of the Judging Instance.
- Points are awarded for correct answers as well as time of submission (earliest=most points)
- Make sure your result is renamed as "answer", use the macro `sendresults` to submit your answers!
