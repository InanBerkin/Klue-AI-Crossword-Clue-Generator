<script>
  import Cell from "./Cell.svelte";
  import { onMount } from "svelte";
  let cwData = getData();
  let newClues = getNewClues();
  let currentTime = new Date().toLocaleString();

  onMount(() => {
    const interval = setInterval(() => {
      currentTime = new Date().toLocaleString();
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  });

  async function getData() {
    let response = await fetch(`http://localhost:3000`);
    let text = await response.json();
    return text;
  }

  async function getNewClues() {
    let response = await fetch(`http://localhost:5000`);
    let clues = await response.json();
    let filtered_clues = clues.map(item => ({
      position: item[2],
      clue: item[1]
    }));

    console.log(clues);

    let newAcross = [];
    let newDown = [];

    filtered_clues.forEach(({ position, clue }) => {
      if (position.charAt(1) === "A") {
        newAcross.push({
          clueNumber: position.charAt(0),
          clueText: clue
        });
      } else if (position.charAt(1) === "D") {
        newDown.push({
          clueNumber: position.charAt(0),
          clueText: clue
        });
      }
    });
    newDown.sort((a, b) => a.clueNumber - b.clueNumber);
    console.log(newDown);

    return { newAcross, newDown };
  }
</script>

<style>
  main {
    display: flex;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }

  @media (min-width: 640px) {
    main {
      max-width: none;
    }
  }
  .grid {
    display: inline-block;
    height: 100%;
    width: 50%;
    text-align: center;
    margin-top: 16px;
    margin-right: 100px;
    margin-left: 100px;
  }

  .row {
    justify-content: center;
    align-items: center;
    display: flex;
    height: 75px;
  }

  .clues {
    display: inline-flex;
    justify-content: start;
    height: 100%;
  }

  .clue-bar {
    display: inline-block;
    margin: 20px;
    margin-top: 0px;
  }

  .clue-section {
    width: 100%;
  }

  .info {
    text-align: end;
    padding: 20px;
  }
</style>

<main>
  {#if cwData === undefined}
    <p />
  {:else}
    {#await cwData}
      <p>Loading crossword...</p>
    {:then value}
      <div class="grid">
        {#each Array(5) as _, i}
          <div class="row">
            {#each Array(5) as _, j}
              <Cell
                number={value.answers[i][j] == null ? null : value.answers[i][j].num}
                text={value.answers[i][j] == null ? null : value.answers[i][j].letter} />
            {/each}
          </div>
        {/each}
        <div class="info">
          <p>Team Name: KLUE</p>
          <p>{currentTime}</p>
        </div>
      </div>
      <div class="clues">
        <div class="clue-section">
          <div class="clue-bar">
            <h2>Across Clues</h2>
            {#each value.clues.acrossClues as clue}
              <p>
                <b>{clue.clueNumber}</b>
                {' '}{clue.clueText}
              </p>
            {/each}
          </div>
          <div class="clue-bar">
            <h2>Down Clues</h2>
            {#each value.clues.downClues as clue}
              <p>
                <b>{clue.clueNumber}</b>
                {' '}{clue.clueText}
              </p>
            {/each}
          </div>
        </div>
        <div class="clue-section">
          {#await newClues}
            Loading new clues...
          {:then value}
            <div class="clue-bar">
              <h2>New Across Clues</h2>
              {#each value.newAcross as clue}
                <p>
                  <b>{clue.clueNumber}</b>
                  {' '}{clue.clueText}
                </p>
              {/each}
            </div>
            <div class="clue-bar">
              <h2>New Down Clues</h2>
              {#each value.newDown as clue}
                <p>
                  <b>{clue.clueNumber}</b>
                  {' '}{clue.clueText}
                </p>
              {/each}
            </div>
          {/await}
        </div>
      </div>
    {:catch error}
      {error.message}
    {/await}
  {/if}
</main>
