<script>
  import Cell from "./Cell.svelte";
  import { onMount } from "svelte";
  let cwData = getData();
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
    console.log(text);
    return text;
  }
</script>

<style>
  main {
    display: flex;
    padding: 1em;
    max-width: 240px;
    margin: 0 auto;
  }

  h1 {
    color: #ff3e00;
    text-transform: uppercase;
    font-size: 4em;
    font-weight: 100;
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
    {:catch error}
      {error.message}
    {/await}
  {/if}
</main>
