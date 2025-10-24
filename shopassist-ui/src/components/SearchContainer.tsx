import { use, useState } from "react";
import { Box, Stack, Textarea, 
    Text, Space, Button, Group, Radio, 
    Select,RangeSlider, Notification} from '@mantine/core';
import { IconX } from '@tabler/icons-react';
import { useProducts } from "../hooks/useProducts";
import type { Product } from "../types/Product";
import { createLogger } from '../utils/logger';
import { ProductGrid } from "./ProductGrid";

export function SearchContainer(){
    const log = createLogger('TestConnectionSection');
    const [radioInput, setRadioInput] = useState(0);
    const [inputId, setInputId] = useState("");
    const [inputCategory, setInputCategory] = useState("");
    const [value, setRangeValue] = useState<[number, number]>([200, 400]);
    const [products, setProducts] = useState<Array<Product>>([]);
    const xIcon = <IconX size={20} />;

    const { isLoading, error, getProductById, getProductsByCategory, getProductsInPriceRange } = useProducts();
    const onSubmit = async () => {
        // Implement search submission logic here

        if (radioInput == 1)
        {
            log.info("SearchContainer by Id: ", inputId);
            const response = await getProductById?.(inputId);
            if (response)
            {
                setProducts([response]);
            }
            // else
            // {
            //     setProducts([]);
            // }
        }
        else if (radioInput == 2)
        {
            log.info("SearchContainer by Category: ", inputCategory);
            const response = await getProductsByCategory?.(inputCategory);
            if (response && response.length >0)
                setProducts(response);
        }
        else if (radioInput == 3)
        {
            log.info("SearchContainer by Price Range: ", value);
            const response = await getProductsInPriceRange?.(value[0], value[1]);
            if (response && response.length >0)
                setProducts(response);
        }
        
        if (error)
        {
            setProducts([]);
            log.error("..SearchContainer API Error: ", error);
        }
    } 
    
    return (
        <Box p="md" className="search-container">
            <Stack w={"100%"}>
                <Group align="end" justify="flex-start">
                    <Radio checked={radioInput ==1} onChange={(event) => {setRadioInput(event.currentTarget.checked?1:0)} } />
                    <Textarea  disabled={isLoading}
                        placeholder="Search by ID"
                        value={inputId}
                        onChange={(e) => {
                            setInputId(e.currentTarget.value);
                            setRadioInput(1);
                        } }
                        className="search-textarea"
                        w={200}
                    /> 
                    <Text size="xs">Search by ID</Text>
                </Group>
                <Group>
                    <Radio checked={radioInput ==2} onChange={(event) => {setRadioInput(event.currentTarget.checked?2:0)} } />
                    <Select
                        w={200}
                        placeholder="Select a category"
                        disabled={isLoading}
                        data={['Smartphones', 'Tables', 'Laptops', 'Headphones']}
                        value={inputCategory}
                        onChange={(value) => {
                            setInputCategory(value || "");
                            setRadioInput(2);
                            }
                        }
                    />
                    <Text size="xs">Search by Category</Text>
                </Group>
                <Group >
                    <Radio checked={radioInput ==3} onChange={(event) => {setRadioInput(event.currentTarget.checked?3:0)} } />
                    <RangeSlider className="price-range-slider"
                        color="violet"
                        min={0}
                        max={500}
                        defaultValue={value}
                        marks={[
                            { value: 100, label: '100' },
                            { value: 200, label: '200' },
                            { value: 400, label: '400' },
                        ]}
                        w={200}
                        onChange={(val) => {
                            setRangeValue(val);
                            setRadioInput(3);
                            }
                        }
                        />
                    <Text size="xs">Search by Price range</Text>
                </Group>
                <Space h="md" />
                <Group justify="left">
                    <Button onClick={() => onSubmit()} disabled={isLoading}>
                        Search
                    </Button>    
                    <Text size="sm" c="dimmed">
                        { isLoading ? "Loading..." : "" }
                    </Text>
                    {
                        error && 
                        (<Notification color="red" hidden={!error} icon={xIcon}>
                            { error }
                        </Notification>)
                    }                    
                </Group>
            </Stack>            
            <ProductGrid products={products} />
        </Box>        
    );
};