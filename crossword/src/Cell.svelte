<script>
  export let text;
  export let number = null;
</script>

<style>
  .cell {
    display: inline-flex;
    width: 75px;
    height: 75px;
    background-color: white;
    justify-content: center;
    align-items: center;
    font-size: 2rem;
    flex-direction: column;
    outline: 3px solid black;
    line-height: 1;
    /* border: 5px solid black; */
  }

  .number {
    display: flex;
    align-self: flex-start;
    font-size: 1rem;
    padding: 4px;
    padding-bottom: 0;
    height: 16px;
  }

  .text {
    vertical-align: middle;
    flex: 2;
  }

  .black {
    background-color: black;
  }
</style>

<!-- markup (zero or more items) goes here -->
{#if text != null}
  <div class="cell">
    <div class="number">
      {#if number != null}{number}{/if}
    </div>
    <span class="text">{text}</span>
  </div>
{:else}
  <div class="cell black" />
{/if}
